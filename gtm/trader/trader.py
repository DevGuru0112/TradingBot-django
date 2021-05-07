from ..api.binance_api_manager import Binance_API_Manager
from ..strategies.v1_strategies import V1Strategies
from ..strategies.v2_strategies import V2Strategies

from .test_trader import TestTrader
from ..strategies.helper import writeFile
from ..data.logger import Logger
from ..data.notifications import NotificationHandler
from ..data.database.model.Coin import Coin
from ..data.database.database_manager import DatabaseManager
from ..scheduler import SafeScheduler

from ..data.database.model.Coin import Coin
from ..data.database.model.Model import Model
from ..data.database.model.Trade import Trade


from pandas.core.common import SettingWithCopyWarning
import time
import warnings
import traceback

import pandas as pd

nh = NotificationHandler()

db_manager = DatabaseManager()


class Trader:
    def __init__(
        self,
        binance_manager: Binance_API_Manager,
        db_manager: DatabaseManager,
        logger: Logger,
    ):
        c = Coin.get("ADA")

        if c == None:
            c = Coin(None, "ADA", 0)
            c.insert()

        self.coin = c
        self.manager = binance_manager
        self.db_manager = db_manager
        self.logger = logger

    def startTrade(self):

        v2strategies = V2Strategies(self.manager, self.coin.gen_parity("USDT"))

        warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

        try:

            spot = self.coin.get_spot()

            trade_history = Trade.get_all_history()

            trader = TestTrader(self.coin, spot, trade_history, "USDT")

            #scheduler = SafeScheduler(self.logger)

            #scheduler.every(10).second.do(v2strategies.ch3mGetSignal)

            while True:

                v2strategies.ch3mGetSignal()

                if v2strategies.df.empty is True:

                    time.sleep(1)

                    continue

                trader.trade(v2strategies.df, v2strategies.signal)

                trader.calculate_profit()

                writeFile("\n= = = = = = = = = = = = = = = = = = = =\n", "output")

                time.sleep(10)

        except Exception as e:
            traceback.print_exception(type(e), e, e.__traceback__)
            self.logger.error(e)
