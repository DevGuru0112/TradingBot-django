from datetime import datetime
from .strategies.helper import *


class TestTrader:
    def __init__(self, parameter: str):
        self.balance = 1000
        self.trade_history = []
        self.coin_balance = 0
        self.parameter = parameter
        self.last_price = 0
        self.last_action = None
        self.loss_sens = 0.005  # 0.5% loss

    def buy(self, price: int, time):

        amount = (self.balance / price) * 9925 / 10000
        self.balance = 0

        self.coin_balance = amount
        self.trade_history.append(
            {"type": "buy", "amount": amount, "price": price, "time": time}
        )

        self.last_action = "buy"

    def sell(self, price: int, time):

        total = self.coin_balance * price
        self.balance = total

        self.coin_balance = 0

        self.trade_history.append(
            {"type": "sell", "amount": total, "price": price, "time": time}
        )

        self.last_action = "sell"

    def calculate_profit(self):

        for i in range(1, len(self.trade_history), 2):

            buy_trade = self.trade_history[i - 1]

            sell_trade = self.trade_history[i]

            writeFile("= = = = = = = = = = = = = = = = = = = = = = = = = = =")

            writeFile(
                "Buy price : {0}, coin_amount : {1}, Time : {2}\n".format(
                    buy_trade["price"], buy_trade["amount"], buy_trade["time"]
                )
            )

            writeFile(
                "Sell price : {0}, balance : {1}, Time : {2}".format(
                    sell_trade["price"], sell_trade["amount"], sell_trade["time"]
                )
            )

            writeFile("= = = = = = = = = = = = = = = = = = = = = = = = = = =")

        wallet_balance = self.balance

        if self.last_action == "buy":
            wallet_balance = self.last_price * self.coin_balance

        profit = (wallet_balance - 1000) / 1000

        writeFile(
            "Total Result :\nWallet Balance : {0}$\nProfit : {1} ".format(
                wallet_balance, profit
            )
        )

    def trade(self, df):

        i = len(df.index) - 1

        score = df["score"][i]
        price = df["close"][i]
        time = df.index[i]

        self.last_price = price

        score_diff = df["score"].diff().fillna(0)

        writeFile(
            "Macd : {0},Rsi : {1},Cci : {2}, Sma : {3}\nScore : {4} -  Score Diff : {5}".format(
                df["macd_score"][i],
                df["rsi_score"][i],
                df["cci_score"][i],
                df["sma_score"][i],
                score,
                score_diff[i],
            )
        )

        if self.last_action == "buy":
            # If profit arrive -0.5%
            # Coin will sell immediately
            bc = self.trade_history[-1]["price"]

            if (price - bc) / bc <= -self.loss_sens:
                self.sell(price, time)

        else:

            if score > 30 and self.balance > 0:
                self.buy(price, time)

            elif 30 >= score > 0 and score_diff[i] > 30 and self.balance > 0:

                self.buy(price, time)

            elif score_diff[i] < -25 and self.coin_balance > 0:
                self.sell(price, time)
