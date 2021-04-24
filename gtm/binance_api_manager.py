from binance.client import Client
from .config import Config

class Binance_API_Manager:

    def __init__(self):
        self.client = Client(Config.API_KEY,Config.API_SECRET_KEY)



