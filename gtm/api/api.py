from .binance_api_manager import Binance_API_Manager
from binance.exceptions import BinanceAPIException
from ..data.database.model.Coin import Coin
from ..data.database.model.Trade import Trade
from ..data.logger import Logger

from datetime import datetime
from binance import client

import time


class Api:

    FEE = 99925 / 100000

    def __init__(
        self, client: Binance_API_Manager, logger: Logger, spot: dict, th: dict
    ):
        self.client = client.client
        self.spot = spot
        self.th = th
        self.logger = logger

    def _get_price(self, symbol: str, isBuy: bool):

        """
        It returns last price of coin respect from orderbook
        @params
            - symbol : str
            - isBuy : bool

        @return
            - price : int
        """

        obt = self.client.get_orderbook_ticker(symbol=symbol)

        return obt["askPrice"] if isBuy else obt["bidPrice"]

    def _order_checker(self, symbol: str, order_id: int):

        """
        It waits until order completed  and return order json

        @params
            - symbol : str
            - order_id : int

        @return
            - order : dict
        """

        while True:
            try:
                order_status = self.client._get_order(symbol=symbol, orderId=order_id)
                return order_status
            except BinanceAPIException as e:

                self.logger.info(e)

                time.sleep(1)

            except Exception as e:
                self.logger.error(f"Unexpected error : {e}")
                time.sleep(1)

    def _try(self, func, *args, **kwargs):

        """
        It retries any function until arrive attempts count
        @params
            - func : function
            - args
            - kwargs

        @return
            - func
        """

        attempts = 0

        max_attempts = kwargs["max_attemps"] or 10

        while attempts < max_attempts:
            try:
                return func(*args, **kwargs)

            except Exception as e:

                self.logger.info(f"Something wrong. Error :{e}")

                if attempts == 0:
                    self.logger.info(e)

                attempts += 1

        return None

    def _quick_limit_order(self, func, symbol: str, coin: Coin):

        """
        It puts an order on the table which given buy an sell function.

        @params
            - func : function (buy & sell)
            - symbol : str
            - coin : Coin

        @return
            - Trade : self
        """

        order = None

        while order is None:

            try:

                price = self._get_price(symbol, False)

                order = func(symbol=str, price=price, quantity=coin.amount)

            except BinanceAPIException as e:
                self.logger.info(e)
                time.sleep(1)

            except Exception as e:
                self.logger.error("Failed to Buy/Sell. Trying Again.")
                time.sleep(1)

        return order

    def buy(self, coin: Coin):

        """
        BUY COIN
        @params
            - coin : Coin

        @return
            - None
        """

        parity = self.spot["usdt"]

        symbol = coin.gen_parity(parity.name)

        order = self._quick_limit_order(self.client.order_market_buy, symbol, parity)

        if order == None:
            return None

        price = order["price"]

        order_id = order["orderId"]

        state = self._order_checker(symbol, order_id)

        if state == None:
            return None

        amount = (parity.amount / price) * Api.FEE

        trade = Trade(None, parity, coin, amount, price)

        coin.amount = amount

        parity.amount = 0

        self._save_trade_action(trade, coin, parity)

    def sell(self, coin: Coin, trade_id: int):

        """
        SELL COIN
        @params
            - coin : Coin
            - trade_id : int

        @return
            - None
        """

        trade = self.th[trade_id]

        parity = self.spot["usdt"]

        symbol = coin.gen_parity(parity.name)

        order = self._quick_limit_order(self.client.order_market_sell, symbol, coin)

        if order == None:
            return None

        price = order["price"]

        order_id = order["orderId"]

        state = self._order_checker(symbol, order_id)

        if state == None:
            return None

        total = coin.amount * price

        coin.amount = 0

        trade.sell(price)

        parity.amount = total

        self._save_trade_action(trade, coin, parity)

    def _save_trade_action(self, trade: Trade, coin: Coin, parity: Coin):

        """
        it saves all changes to list of trades and spot
        @params
            - trade : Trade
            - coin : Coin
            - parity : Coin

        @return
            - None
        """

        coin.save()
        trade.save()
        parity.save()

        self.th[trade.id] = trade
        self.spot[coin.name] = coin
        self.spot["usdt"] = parity
