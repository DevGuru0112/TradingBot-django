from .config import Config
from binance.client import Client
from .binance_api_manager import Binance_API_Manager
from .scheduler import SafeScheduler
from .trader import Trader
import time


class Server:
    
    



    def start(self):
        
        manager = Binance_API_Manager()

        
        trader = Trader(manager) 
        # schedule = SafeScheduler()


        trader.startTrade()
        # while True:

            

        #     print("----")
            
        #     time.sleep(10)

            




