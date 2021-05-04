from datetime import datetime
from .Model import Model
import json


class Trade(Model):

    column_name = "trade_history"

    def __init__(
        self,
        _id,
        buy_parity,
        sell_parity,
        amount,
        buy_price,
        buy_time,
        sell_time,
        sell_price,
        result,
        profit,
    ):

        super().__init__()
        self.id = _id if _id != None else None
        self.buy_parity = buy_parity
        self.sell_parity = sell_parity
        self.amount = amount
        self.buy_price = buy_price
        self.buy_time = (
            buy_time
            if buy_time != None
            else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        self.sell_time = None
        self.sell_price = None
        self.result = None

    def sell(self, sell_price, result):

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
        self.result = result
        self.sell_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.profit = self.calculate_profit(self.buyP, sellP) if sellP != None else None

        return self

    def calculate_profit(self, buy, sell):
        return ((sell - buy) / buy) * 100

    def toJson(self):

        return {
            "buy_parity": self.buy_parity,
            "sell_parity": self.sell_parity,
            "buy_price": self.buy_price,
            "buy_time": self.buy_time,
            "amount": self.amount,
            "sell_price": self.sell_price,
            "sell_time": self.sell_time,
            "result": self.result,
            "profit": self.profit,
        }

    def insert(self):

        """
        This function inserts Trade into the database.
        @params
            - None

        @return
            - Trade : self
        """

        dict_form = self.to_json()

        self.trade_history.insert_one(dict_form)

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
        return {}
