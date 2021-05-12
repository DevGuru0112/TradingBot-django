from gtm.data.database.model.Coin import Coin
from bson.objectid import ObjectId
from ..data.data import Data
from ..strategies.stream_strategy import StreamStrategy
from ..strategies.strategy_helper import get_candle_property
from ..data.config import Config
from ..data.database.model.Trade import Trade

from ..strategies.helper import writeFile

from datetime import datetime
import traceback


FEE = 99925 / 100000


class AutoTestTrader:
    def __init__(self, strategy: StreamStrategy):
        self.strategy = strategy

    def _buy(self, coin: Coin, price: int, amount: int):

        """
        This function handle buy request.
        Buy functionality is not connected binance api.
        Wallet is fake. Goal is testing these implementations

        @params
            - price (current price of this token) : int
            - time : datetime

        @return
            - None

        """

        a = (amount / price) * FEE

        bridge = Data.spot[Config.BRIDGE]

        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        trade = Trade(None, Config.BRIDGE, coin.name, a, price, time)

        trade.insert()

        trade_id = str(trade.id)

        bridge.amount -= amount
        coin.amount += a

        coin.open_trades.append(trade_id)

        # control updatedModelObject updatesuccess State
        bridge.save()
        coin.save()

        Data.th[trade_id] = trade
        Data.spot[coin.name] = coin
        Data.spot[Config.BRIDGE] = bridge

        info = (
            f"----------------------------------------------------\n"
            f"coin name : {coin.name} , type : BUY\n"
            f"coin amount : {a} , price : {price}, amount : {coin.amount}\n"
            f"Left bridge : {bridge.amount}\n"
        )

        writeFile(info, "output")

        # Data.nh.send_notification(info)

    def _sell(self, coin, price: int, amount: int, _id=None):

        """
        This function handle sell request.
        Sell functionality is not connected binance api.
        Wallet is fake. Goal is testing these implementations

        @params
            - price (current price of this token) : int
            - time : datetime

        @return
            - None

        """

        bridge = Data.spot[Config.BRIDGE]

        total = amount * price * FEE

        if coin.amount == amount:

            # close all position in this coin
            for _id in coin.open_trades:

                Data.th[_id].sell(price)

                Data.th[_id].save()

            coin.open_trades.clear()

        else:

            # close specify position in this coin

            Data.th[_id].sell(price)

            Data.th[_id].save()

            coin.open_trades.remove(_id)

        coin.amount -= amount
        bridge.amount += total

        coin.save()
        bridge.save()

        Data.spot[Config.BRIDGE] = bridge
        Data.spot[coin.name] = coin
        
        Data.th[_id]
        info = (
            f"----------------------------------------------------\n"
            f"coin name : {coin.name} , type : SELL \n"
            f"total : {total} , price : {price}\n"
            f"amount : {amount}, left coin : {coin.amount}\n"
            f"profit : {}"
        )

        writeFile(info, "output")

        # Data.nh.send_notification(info)

    def trade(self):

        """
        This function make buy & sell action depend on signal
        which is created from getsignal function.


        Buy Conditions :

        - Signal = BUY & already has bridge

        Sell Conditions :

        - Signal = SELL & already has coin

        - profit of open trade is negative and lower than expected.
          (only close spesific trade amount)

        @params
            - df (includes score column) : Dataframe

        @return
            - None
        """

        # pairs of candles
        poc = Data.poc

        spot = Data.spot

        th = Data.th

        signals = Data.signals

        bridge_amount = spot[Config.BRIDGE].amount

        for pair in poc:

            # pair analyzer and current buy&sell signal
            signal = signals.get(pair)

            if signal == None:
                continue

            # dataframe of selected pair
            df = poc[pair]

            candle_property = get_candle_property(df)

            price = df["close"].iloc[-1]

            coin_name = pair[: len(pair) - 4]

            coin = spot[coin_name]

            coin_amount = coin.amount

            for _id in coin.open_trades:

                open_trade = th[_id]

                bp = open_trade.buy_price

                profit = (price - bp) * 100 / bp

                if profit < -2:

                    amount = open_trade.amount
                    # sell time because loss is higher than expcected

                    total = amount * price

                    if total >= 10:
                        try:
                            self._sell(coin, price, amount, _id)
                        except:
                            traceback.print_exc()

            if signal == "BUY" and bridge_amount > 0:

                amount = bridge_amount / 4

                if amount >= 10:
                    try:
                        self._buy(coin, price, amount)
                    except:
                        traceback.print_exc()

            if signal == "SELL" and coin_amount > 0:

                total = coin_amount * price
                if total > 10:

                    try:
                        self._sell(coin, price, coin_amount)
                    except:
                        traceback.print_exc()