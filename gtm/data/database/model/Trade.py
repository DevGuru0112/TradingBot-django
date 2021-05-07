from datetime import datetime
from .Model import Model
from .Coin import Coin
import json

fee = 99925 / 100000  # 0.075 fee


class Trade(Model):

    column_name = "trade_history"

    def __init__(
        self,
        _id,
        bridge: Coin,
        coin: Coin,
        amount,
        buy_price,
        buy_time=None,
        sell_time=None,
        sell_price=None,
        result=None,
        profit=None,
    ):

        super().__init__()
        self.id = _id if _id != None else None
        self.coin = coin.name
        self.bridge = bridge.name
        self.amount = amount
        self.buy_price = buy_price

        self.buy_time = (
            buy_time
            if buy_time != None
            else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        self.sell_time = sell_time
        self.sell_price = sell_price
        self.result = result
        self.profit = profit

    def sell(self, sell_price):

        """
        This function adds sell point attributes to the
        instance and calculate profit of this trade action as a
        result of that
        @params
            - sell_price : int
            - result : int

        @return
            - Trade : self
        """

        self.sell_price = sell_price

        self.result = self.amount * sell_price

        self.sell_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.profit = (
            self.calculate_profit(self.buy_price, sell_price)
            if sell_price != None
            else None
        )

        return self

    def calculate_profit(self, buy, sell):
        return ((sell - buy) / buy) * 100

    def insert(self):

        """
        This function inserts Trade into the database.
        @params
            - None

        @return
            - Trade : self
        """
        

        dict_form = self.to_json()

        self.id = self.trade_history.insert_one(dict_form).inserted_id

        return self

    @staticmethod
    def get_all_history():

        """
        This function gets all trades from database. Then , creates instances of these trades and returns
        @params
            - None

        @return
            - list : (an array which is inside Trades)
        """

        cursor = Trade.get_all()

        th_list = Trade.from_jsons(cursor)

        return th_list

    @staticmethod
    def get():
        """
        This function gets single Trade record from database and return query result.
        @params
            - None

        @return
            - Coin
        """

        query_dict = {}
        coin = Model.get(query_dict, "trade_history")
        return Trade.from_json(coin)

    def to_json(self):

        return {
            "coin": self.coin,
            "bridge": self.bridge,
            "buy_price": self.buy_price,
            "buy_time": self.buy_time,
            "amount": self.amount,
            "sell_price": self.sell_price,
            "sell_time": self.sell_time,
            "result": self.result,
            "profit": self.profit,
        }
