from .data.config import Config
from binance.client import Client
from .trader.binance_api_manager import Binance_API_Manager
from .data.database.database_manager import DatabaseManager
from .scheduler import SafeScheduler
from .trader.trader import Trader
import time


class Server:

    def start(self):

        manager = Binance_API_Manager()

        db_manager = DatabaseManager()

        trader = Trader(manager,db_manager)
        
        print("Server Started\n")

        trader.startTrade()
