from binance.client import Client
from ..data.logger import Logger
from ..data.config import Config
from ..api.api import Api
from ..strategies.analyzers.analyzerUtils import AnalyzerUtils
from datetime import datetime
from ..strategies.stream_strategy import StreamStrategy
from ..data.data import Data


import json
import websockets
import asyncio as aio
import pandas as pd


class Explore:

    # pairs_of_candles

    def __init__(self, api: Api, client: Client, logger: Logger):
        self.client = client
        self.logger = logger
        self.api = api
        self.strategy = StreamStrategy(limit=20)

    async def _candle_stick_data(self, fp: str, op: str, queue):

        url = "wss://stream.binance.com:9443/ws/"  # steam address

        async with websockets.connect(url + fp) as sock:

            await sock.send(op)

            while True:

                resp = await sock.recv()

                if "result" in resp:
                    continue

                pair = json.loads(resp)

                kline = pair["k"]

                self._update_dataframe(kline)

                queue.put_nowait("True")

    async def scan_market(self, interval: str, func):

        km = f"@kline_{interval}"

        pairs = [p.lower() + km for p in Config.PAIRS]

        fp = pairs[0] + km

        op = pairs[1:]

        d = {"method": "SUBSCRIBE", "params": pairs, "id": 1}

        op = json.dumps(d)

        self._get_multiple_candles(Config.PAIRS, interval)

        queue = aio.Queue()

        loop = aio.get_event_loop()

        trade_block = loop.run_in_executor(None, func, loop, queue)

        scan_block = loop.create_task(self._candle_stick_data(fp, op, queue))

        while True:

            try:

                message = await queue.get()

            except:
                break

        loop.stop()

    def _get_multiple_candles(self, pairs: list, interval: str):

        candles = {}

        for pair in pairs:

            candle = self.api.get_candles(symbol=pair, interval=interval, limit=20)

            if candle == None:
                # if tries get candle for 20 times but couldn't fetched
                pass

            candles[pair] = AnalyzerUtils.convert_to_dataframe(candle)

        Data.poc = candles

    def _update_dataframe(self, d: dict):

        symbol = d["s"]

        okt = d["t"]

        df = Data.poc[symbol]

        ckt = int(df.iloc[-1, df.columns.get_loc("opentimeStamp")])

        row_values = {
            "opentimeStamp": int(okt),
            "open": float(d["o"]),
            "high": float(d["h"]),
            "low": float(d["l"]),
            "close": float(d["c"]),
            "volume": float(d["v"]),
            "closetimeStamp": float(d["T"]),
            "quote_asset_volume": float(d["q"]),
            "number_of_trades": int(d["n"]),
            "tbb_asset_volume": float(d["V"]),
            "tbq_asset_volume": float(d["Q"]),
            "ignored": float(d["B"]),
        }

        if ckt != okt:
            # new row
            df = df.iloc[1:]
        else:
            # update row
            df = df.iloc[:-1]

        df.loc[len(df.index)] = row_values

        df.index = df.opentimeStamp.apply(
            lambda x: pd.to_datetime(datetime.fromtimestamp(x / 1000).strftime("%c"))
        )

        self.strategy.ch3mGetSignal(df, symbol)
