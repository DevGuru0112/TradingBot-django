from ..strategies.v2_strategies import V2Strategies

from .test_trader import TestTrader
from ..strategies.helper import writeFile
from ..data.database.model.Coin import Coin
from ..data.database.model.Coin import Coin
from ..data.database.model.Trade import Trade
from pandas.core.common import SettingWithCopyWarning

from ..data.data import Data
from ..api.api import Api
from ..data.config import Config

import time
import warnings
import traceback


class Trader:
    def __init__(self):
        c = Coin.get("ADA")

        if c == None:
            c = Coin(None, "ADA", 0)
            c.insert()

        self.coin = c
        self.manager = Data.bm
        self.db_manager = Data.db
        self.logger = Data.logger["server"]

        self.api = Api(Data.bm.client, self.logger)

    def startTrade(self):

        v2strategies = V2Strategies(
            self.manager, self.coin.generate_pair(Config.BRIDGE)
        )

        warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

        try:

            spot = self.coin.get_spot()

            trade_history = Trade.get_all_history()

            trader = TestTrader(self.coin, spot, trade_history, Config.BRIDGE)

            while True:

                df = self.api.get_candles(
                    self.coin.generate_pair(Config.BRIDGE),
                    self.manager.client.KLINE_INTERVAL_3MINUTE,
                    20,
                )

                v2strategies.ch3mGetSignal(df)

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
