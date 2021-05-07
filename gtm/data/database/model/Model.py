from ..database_manager import DatabaseManager
import json
from ....trader import trader
from bson import json_util, ObjectId


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
        """
        This function gets single record from database and return query result.
        @params
            - query
            - column_name

        @return
            - query_result : Query
        """
        db = trader.db_manager.client["binance_gtm"]

        query_result = db[col].find_one(query)

        return query_result

    def to_json(self):
        return json.dumps(self.__dict__)

    def save(self):

        """
        This function changes pre-object which is on database with new object.
        @params
            - None
        @return
            - update_result : pymongo.results.UpdateResult
        """

        column_name = self.__class__.column_name

        col = self.__getattribute__(column_name)

        query = {"_id": ObjectId(self.id)}

        updated = {"$set": self.to_json()}

        update_result = col.update_one(query, updated)
        return update_result

    @classmethod
    def get_all(cls):

        """
        This function changes pre-object which is on database with new object.
        @params
            - None
        @return
            - update_result : pymongo.results.UpdateResult
        """
        
        column_name = cls.column_name

        col = Model().__getattribute__(column_name)

        all_docs = col.find()

        return all_docs

    @classmethod
    def from_json(cls, cursor):

        """
        This function converts string json to dict. After that,
        create single instance by using values which is inside this dict
        @params
            - cls : class (auto provided)
            - cursor : CursorObject
        @return
            - object : (generated given classname)
        """

        json_str = json.dumps(
            cursor, sort_keys=True, indent=4, default=json_util.default
        )

        json_data = json.loads(json_str)

        json_data["_id"] = json_data["_id"]["$oid"]

        return cls(**json_data)

    @classmethod
    def from_jsons(cls, cursor):

        """
        This function converts string json to dict. After that,
        create multiple instances by using values which is inside this dict
        @params
            - cls : class (auto provided)
            - cursor : CursorObject
        @return
            - array : (an array which is inside instances)
        """

        if cursor != None:
            clist = []

            for cs in cursor:
                clist.append(cls(**cs))

            return clist

        else:
            return None