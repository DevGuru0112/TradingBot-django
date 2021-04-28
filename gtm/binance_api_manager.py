from binance.client import Client
from .config import Config
from .logger import Logger


logger = Logger("api")


class Binance_API_Manager:
    def __init__(self):

        while True:
            
            try:
                self.client = Client(Config.API_KEY, Config.API_SECRET_KEY)
            except Exception as e:
                logger.error(e)
                continue

            break