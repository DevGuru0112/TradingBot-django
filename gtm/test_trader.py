from datetime import datetime
from .strategies.helper import writeFile
from .logger import Logger
from .notifications import NotificationHandler


logger = Logger("test_trader")
nh = NotificationHandler()


class TestTrader:
    def __init__(self, parameter: str):
        self.balance = 1000
        self.trade_history = []
        self.coin_balance = 0
        self.parameter = parameter
        self.last_price = 0
        self.last_action = None
        self.loss_sens = 0.0005  # 0.5% loss
        self.fee = 99925 / 100000  # 0.075 fee

    def buy(self, price: int, time):

        """
        This function handle buy request.
        Buy functionality is not connected binance api.
        Wallet is fake. Goal is testing these implementations

        @params
            - price (current price of this token) : int
            - time : datetime

        @return
            - None

        """

        amount = (self.balance / price) * self.fee  # 0.075 fee
        self.balance = 0

        self.coin_balance = amount
        self.trade_history.append(
            {"type": "buy", "amount": amount, "price": price, "time": time}
        )

        self.last_action = "buy"

    def sell(self, price: int, time):

        """
        This function handle sell request.
        Sell functionality is not connected binance api.
        Wallet is fake. Goal is testing these implementations

        @params
            - price (current price of this token) : int
            - time : datetime

        @return
            - None

        """

        total = (self.coin_balance * price) * self.fee  # 0.075 fee

        self.balance = total

        self.coin_balance = 0

        self.trade_history.append(
            {"type": "sell", "amount": total, "price": price, "time": time}
        )

        self.last_action = "sell"

    def calculate_profit(self):

        """
        This function calculate profit after buy and sell requests.
        The result of that writes a file which is called by output.txt

        @params
            - None

        @return
            - None
        """

        for i in range(1, len(self.trade_history), 2):

            buy_trade = self.trade_history[i - 1]

            sell_trade = self.trade_history[i]

            info = (
                "\n= = = = = = = = = = = = = = = = = = =\n"
                "Buy price : {0}, coin_amount : {1}, Time : {2}\n"
                "Sell price : {3}, balance : {4}, Time : {5}"
                "\n= = = = = = = = = = = = = = = = = = =\n".format(
                    buy_trade["price"],
                    buy_trade["amount"],
                    buy_trade["time"],
                    sell_trade["price"],
                    sell_trade["amount"],
                    sell_trade["time"],
                )
            )

            nh.send_notification(info)

            writeFile(info)

        wallet_balance = self.balance

        if self.last_action == "buy":
            wallet_balance = self.last_price * self.coin_balance * self.fee

        profit = (wallet_balance - 1000) / 10

        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        info = f"\nTotal Result : \nWallet Balance : {wallet_balance}$\nProfit : {profit}%\nCurrent Time : {time}"

        nh.send_notification(info)

        writeFile(info)

    def trade(self, df):

        """
        This function check instant score of coin at current condition.
        If it is proper to buy. it calls buy function.
        If it is proper to sell and already have its . it calls sell function.

        @params
            - df (includes score column) : Dataframe

        @return
            - None
        """

        i = len(df.index) - 1

        score = df["score"][i]
        price = df["close"][i]
        time = df.index[i].strftime("%Y-%m-%d %H:%M:%S")

        self.last_price = price

        score_diff = df["score"].diff().fillna(0)

        info = "\n= = = = = = = = = = = = = = = = = = =\n" "Macd : {0},Rsi : {1},Cci : {2}, Sma : {3}\nScore : {4} -  Score Diff : {5}\n".format(
            df["macd_score"][i],
            df["rsi_score"][i],
            df["cci_score"][i],
            df["sma_score"][i],
            score,
            score_diff[i],
        )

        writeFile(info)
        nh.send_notification(info)

        if self.last_action == "buy":

            # If profit arrive -0.5%
            # Coin will sell immediately
            bc = self.trade_history[-1]["price"]

            if (price - bc) / bc <= - self.loss_sens:
                self.sell(price, time)

        else:

            if score > 30 and self.balance > 0:
                self.buy(price, time)

            elif 30 >= score > 0 and score_diff[i] > 30 and self.balance > 0:

                self.buy(price, time)

            elif score_diff[i] < -15 and self.coin_balance > 0:
                self.sell(price, time)
