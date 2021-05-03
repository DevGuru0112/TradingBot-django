from ..database_manager import DatabaseManager
import json
from ....trader import trader
from bson import json_util,ObjectId


class Model:
    def __init__(self):
        self.id = None
        self.client = trader.db_manager.client
        self.db = self.client["binance_gtm"]
        self.spot_wallet = self.db["spot_wallet"]
        self.trade_history = self.db["trade_history"]

    def insert(self):
        pass

    @staticmethod
    def get(query, col):

        db = trader.db_manager.client["binance_gtm"]

        query = db[col].find_one(query)

        return query

    def to_json(self):
        return json.dumps(self.__dict__)

    def save(self):
        column_name = self.__class__.column_name

        col = self.__getattribute__(column_name)

        query = {"_id": ObjectId(self.id)}

        updated = {"$set": self.to_json()}

        update_result = col.update_one(query, updated)

        return update_result
        

    @classmethod
    def from_json(cls, cursor):
        json_str = json.dumps(
            cursor, sort_keys=True, indent=4, default=json_util.default
        )

        json_data = json.loads(json_str)
        return cls(**json_data)