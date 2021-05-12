from .data.config import Config
from .api.binance_api_manager import Binance_API_Manager
from .data.database.database_manager import DatabaseManager
from .trader.auto_trader import AutoTrader
from .data.logger import Logger
from .data.data import Data
from .data.notifications import NotificationHandler


class Server:
    def __init__(self):
        pass

    def start(self):
        Config.read_config()

        Data.logger["server"] = Logger("server")
        Data.logger["database"] = Logger("database")

        Data.nh = NotificationHandler()

        Data.bm = Binance_API_Manager()
        Data.db = DatabaseManager()

        trader = AutoTrader()

        
        
        print("Server Started\n")

        trader.start()
