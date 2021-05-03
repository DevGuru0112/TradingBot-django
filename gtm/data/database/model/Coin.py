from .Model import Model
import json


class Coin(Model):

    column_name = "spot_wallet"

    def __init__(self, _id, name, amount):
        super().__init__()
        self.name = name
        self.amount = amount
        self.id = _id["$oid"] if _id != None else None


    @staticmethod
    def get(coin_name):
        query_dict = {"name": coin_name}
        coin = Model.get(query_dict, "spot_wallet")

        if coin == None:
            return None
        else:
            return Coin.from_json(coin)

    def insert(self):

        coin = Coin.get(self.name)


        if coin == None:
            self.spot_wallet.insert_one({"name": self.name, "amount": self.amount})
        else:
            self.id = coin.id
            coin.amount += self.amount
            self.save()

        return self

    def to_json(self):
        return {"name": self.name, "amount": self.amount}

    def gen_parity(self, parity):

        return self.name + parity
