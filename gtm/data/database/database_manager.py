from pymongo import MongoClient
from pymongo.errors import *
from ..config import Config
from pprint import pprint
from ..logger import Logger
import traceback


logger = Logger("database")

class DatabaseManager:

    def __init__(self):
        
        while True:
            
            try : 
                self.client = MongoClient(Config.MONGO_URI)
                self.db = self.client["binance_gtm"]

            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
                logger.error(e)
                continue
            
            break

