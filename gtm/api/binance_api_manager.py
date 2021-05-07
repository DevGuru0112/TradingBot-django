from binance.client import Client
from ..data.config import Config
from ..data.logger import Logger

import traceback

logger = Logger("api")


class Binance_API_Manager:
    def __init__(self):

        while True:

            try:
                self.client = Client(Config.API_KEY, Config.API_SECRET_KEY)
            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
                logger.error(e)
                continue

            break