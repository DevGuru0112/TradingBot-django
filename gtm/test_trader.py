from datetime import datetime


class TestTrader:
    def __init__(self, parameter: str):
        self.balance = 1000
        self.trade_history = []
        self.coin_balance = 0
        self.parameter = parameter
        self.last_price = 0

    def buy(self, price: int, time):

        amount = (self.balance / price) * 9925 / 10000
        self.balance = 0

        self.coin_balance = amount
        self.trade_history.append(
            {"type": "buy", "amount": amount, "price": price, "time": time}
        )

        self.last_price = price

    def sell(self, price: int, time):

        total = self.coin_balance * price
        self.balance = total

        self.coin_balance = 0

        self.trade_history.append(
            {"type": "sell", "amount": total, "price": price, "time": time}
        )

        self.last_price = price

    def calculate_profit(self):

        for i in range(1, len(self.trade_history), 2):

            buy_trade = self.trade_history[i - 1]

            sell_trade = self.trade_history[i]

            print("= = = = = = = = = = = = = = = = = = = = = = = = = = =")

            print(
                "Buy price : {0}, coin_amount : {1}, Time : {2}\n".format(
                    buy_trade["price"], buy_trade["amount"], buy_trade["time"]
                )
            )
            print(
                "Sell price : {0}, balance : {1}, Time : {2}".format(
                    sell_trade["price"], sell_trade["amount"], sell_trade["time"]
                )
            )

            print("= = = = = = = = = = = = = = = = = = = = = = = = = = =")

        wallet_balance = self.balance

        print(self.last_price)
        if len(self.trade_history) % 2 != 0:
            print("sl")
            print(self.last_price * self.coin_balance)
            wallet_balance = self.last_price * self.coin_balance

        profit = (wallet_balance - 1000) / 1000

        print(
            "Total Result :\nWallet Balance : {0}$\nProfit : {1} ".format(
                wallet_balance, profit
            )
        )

    def trade(self,df):
        
        i = len(df.index) - 1 
        score = df["score"][i]
        price = df["close"][i]

        score_diff = df["score"].diff().fillna(0)

        print(score_diff[i])

        df["score_diff"] = score_diff

        time = df.index[i]
        if score > 50 and self.balance > 0:
            self.buy(price, time)

        # elif score < -35 and self.coin_balance > 0:
        #     print("score_standart_sell")
        #     self.sell(price)

        elif 50 >= score > 0 and score_diff[i] > 30 and self.balance > 0:
            
            self.buy(price, time)

        elif score_diff[i] < -25 and self.coin_balance > 0:
            self.sell(price, time)
