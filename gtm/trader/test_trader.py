from datetime import datetime
from ..strategies.helper import writeFile
from ..data.logger import Logger
from ..data.notifications import NotificationHandler
from ..data.database.model.Trade import Trade
from ..strategies.strategy_helper import get_candle_property


logger = Logger("test_trader")
nh = NotificationHandler()


fee = 99925 / 100000  # 0.075 fee
loss_sens = 0.0005  # 0.5% loss


class TestTrader:
    def __init__(self, coin, spot, trade_history, parity):
        self.trade_history = trade_history
        self.spot = spot
        self.coin = coin
        self.parity = spot[parity]
        self.last_price = 0
        self.last_action = None

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

        amount = (self.parity.amount / price) * fee  # 0.075 fee

        self.usdt = 0

        trade = Trade(None, self.coin.name, self.parity.name, amount, price)

        self.parity.amount = 0
        self.coin.amount = amount

        self.parity.save()
        self.coin.save()
        trade.insert()

        # self.spot["wallet"] = {
        #     self.coin.parity: {"amount": 0},
        #     self.coin.name: {"amount": amount},
        # }

        self.trade_history.append(trade)

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

        total = (self.coin.amount * price) * fee  # 0.075 fee

        self.parity.amount = total

        self.coin.amount = 0

        last_trade = self.trade_history[-1]

        last_trade.sell(price, total)

        last_trade.save()

        self.coin.save()

        self.parity.save()

        self.trade_history[-1] = last_trade

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

        wallet_balance = self.parity.amount

        if wallet_balance == 0:
            wallet_balance = self.last_price * self.coin.amount * fee

        profit = (wallet_balance - 1000) / 10

        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        info = f"\nTotal Result : \nWallet Balance : {wallet_balance}$\nProfit : {profit}%\nCurrent Time : {time}"

        writeFile(info, "output")

        nh.send_notification(info)

    def trade(self, df, signal):

        """
        This function check instant score of coin at current condition.
        If it is proper to buy. it calls buy function.
        If it is proper to sell and already have its . it calls sell function.

        @params
            - df (includes score column) : Dataframe

        @return
            - None
        """

        candle_property = get_candle_property(df)

        coin_amount = self.coin.amount

        parity_amount = self.parity.amount

        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        price = df["close"].iloc[-1]

        if signal == "BUY" and parity_amount > 0:

            self.buy(price, time)

        if signal == "SELL" and coin_amount > 0:

            self.sell(price, time)

        bp = self.trade_history[-1].buy_price
        profit = (price - bp) * 100 / bp

        if profit < candle_property["nm"] * 3 and coin_amount > 0:

            self.sell(price, time)
