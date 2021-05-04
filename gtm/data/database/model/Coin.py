from .Model import Model
import json


class Coin(Model):

    column_name = "spot_wallet"

    def __init__(self, _id, name, amount):
        super().__init__()
        self.name = name
        self.amount = amount
        self.id = _id if _id != None else None

    @staticmethod
    def get(coin_name):
        """
        This function gets single Coin record from database and return query result.
        @params
            - coin_name : str

        @return
            - Coin
        """

        query_dict = {"name": coin_name}
        coin = Model.get(query_dict, "spot_wallet")

        if coin == None:
            return None
        else:
            return Coin.from_json(coin)

    def insert(self):

        """
        This function inserts Coin into the database. If already is inserted, then saves this coin via new changes.
        @params
            - None

        @return
            - Coin
        """

        coin = Coin.get(self.name)

        if coin == None:
            self.spot_wallet.insert_one({"name": self.name, "amount": self.amount})
        else:
            self.id = coin.id
            coin.amount += self.amount
            self.save()

        return self

    def get_spot(self):

        """
        This function gets all coins from database. Then , creates instances of these coins and returns
        @params
            - None

        @return
            - list : (an array which is inside Coins)
        """

        cursor = self.get_all()

        spot_list = Coin.from_jsons(cursor)

        spot_dict = {c.name: c for c in spot_list}

        return spot_dict

    def to_json(self):
        return {"name": self.name, "amount": self.amount}

    def gen_parity(self, parity):
        """
        This function generate coin/parity conjugate. Example : BTC -> USDT :  BTCUSDT
        @params
            - parity : str

        @return
            - parity conjugate : str
        """
        return self.name + parity
