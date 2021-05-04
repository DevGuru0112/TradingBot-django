from .binance_api_manager import Binance_API_Manager
from ..strategies.v1_strategies import V1Strategies
from .test_trader import TestTrader
from ..strategies.helper import writeFile
from ..data.logger import Logger
from ..data.notifications import NotificationHandler
from ..data.database.model.Coin import Coin
from ..strategies.helper import *
from ..data.database.database_manager import DatabaseManager


from ..data.database.model.Coin import Coin
from ..data.database.model.Model import Model
from ..data.database.model.Trade import Trade


from pandas.core.common import SettingWithCopyWarning
import time
import warnings
import traceback

import pandas as pd

logger = Logger("trader")
nh = NotificationHandler()

db_manager = DatabaseManager()


class Trader:
    def __init__(
        self, binance_manager: Binance_API_Manager, db_manager: DatabaseManager
    ):
        c = Coin.get("DOGE")

        if c == None:
            c = Coin(None, "DOGE", 0)
            c.insert()

        self.coin = c
        self.manager = binance_manager
        self.db_manager = db_manager

    def startTrade(self):

        v1strategies = V1Strategies(self.manager, self.coin.gen_parity("USDT"))

        warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

        try:

            spot = self.coin.get_spot()

            trade_history = Trade.get_all_history()

            trader = TestTrader(self.coin, spot, trade_history, "USDT")

            while True:

                ch3_df = v1strategies.ch3mGetSignal()

                if ch3_df.empty is True:

                    time.sleep(1)

                    continue

                trader.trade(ch3_df)

                trader.calculate_profit()

                writeFile("\n= = = = = = = = = = = = = = = = = = = =\n", "output")

                time.sleep(10)

        except Exception as e:
            traceback.print_exception(type(e), e, e.__traceback__)
            logger.error(e)
