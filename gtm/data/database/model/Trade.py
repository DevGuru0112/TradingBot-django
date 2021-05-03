from datetime import datetime
from .Model import Model
import json


class Trade(Model):

    column_name = "trade_history"

    def __init__(self, amount, buyP):
        self.amount = amount
        self.buyP = buyP
        self.buyD = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.sellD = None
        self.sellP = None
        self.total = None

    def sell(self, sellP, total):
        self.sellP = sellP
        self.total = total
        self.sellD = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.profit = self.calculate_profit(self.buyP, sellP) if sellP != None else None

        return self

    def calculate_profit(self, buy, sell):
        return ((sell - buy) / buy) * 100

    def toJson(self):

        return {
            "buy_price": self.buyP,
            "buy_time": self.buyD,
            "amount": self.amount,
            "sell_price": self.sellP,
            "sell_time": self.sellD,
            "result": self.total,
        }

    def insert(self):
        json_str = json.dumps(self.__dict__)
        self["trade_history"].insert_one(json_str)

    @staticmethod
    def get(id):
        query_dict = {}
        coin = Model.get(query_dict, "trade_history")
        return Trade.from_json(coin)

    @staticmethod
    def decode(trade_history):

        ths = []

        for th in trade_history:
            trade = Trade(th["amount"], th["buyP"])
            trade.sell(th["sellP"], th["total"])
            ths.append(trade)

        return ths
