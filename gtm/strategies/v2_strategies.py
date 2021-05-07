from ..api.binance_api_manager import Binance_API_Manager
from binance.exceptions import BinanceAPIException, BinanceRequestException
from datetime import datetime
from .analyzers.indicators import Indicators
from ..data.logger import Logger
from binance.client import Client
from .helper import writeFile

import traceback

import pandas as pd

logger = Logger("strategies")


class V2Strategies:
    def __init__(self, binance_manager: Binance_API_Manager, symbol):
        self.client = binance_manager.client
        self.symbol = symbol
        self.limit = 101

    def ch3mGetSignal(self):

        sp = 5
        sph = sp / 2

        signal = None

        # GENERATE SEQUENTLY CHAIN MODEL (THINK ABOUT IT)

        # example: first RSI and CCI controlling and generating a score for depending on movement
        # after that MACD Controlling and generating a score depending on movement with RSI/CCI score !!!

        # TODO #1 => calculate all of 3m row changes. And calculate how much increase klines
        # TODO #1 => and how much decrease klines which is determined on interval.
        # TODO #1 => calculate all of increased klines average. Example 0.25% increase is average of all increased klines.
        # TODO #1 => if current increase value is bigger than average. It is possible going up

        # TODO #2 => Calculate sma-21 / sma-51 difference if sma-21 crossing sma-51 on positive direction, good opportunity to buy
        # TODO #2 => if MACD is support this state, it can be provide early buy opportunity.
        # TODO #2 => RSI is good indicator for finding selling point. If rsi greater than 70, any decreasing moment is good to sell.

        df = None

        try:
            # If goes something wrong! return none
            df = self.client.get_klines(
                symbol=self.symbol,
                interval=Client.KLINE_INTERVAL_3MINUTE,
                limit=self.limit,
            )

        except (BinanceAPIException, BinanceRequestException) as e:

            traceback.print_exception(type(e), e, e.__traceback__)
            logger.error(e)

            return pd.DataFrame()

        indicators = Indicators(self.symbol, df)

        df = indicators.calculate(sma1=9, sma2=21)

        df_list = df.itertuples(index=True)

        ## MACD Variables

        macd_delta_diff = df["macd_delta"].diff().fillna(0)

        sorted_d = macd_delta_diff.sort_values().tolist()

        ## RSI Variables

        rsi_diffs = df["rsi"].diff().fillna(0)
        sorted_rsi_diffs = rsi_diffs.sort_values().tolist()

        ## CCI Variables

        cci_diffs = df["cci"].diff().fillna(0)
        sorted_cci_diffs = cci_diffs.sort_values().tolist()

        ## SMA Variables

        # delta_sma = df["sma_10"] - df["sma_20"]

        sma_diffs = df["sma_9"].diff().fillna(0)

        sorted_sma_diffs = sma_diffs.sort_values().tolist()

        df["score"] = 0
        df["sma_score"] = 0
        df["rsi_score"] = 0
        df["cci_score"] = 0
        df["macd_score"] = 0

        # ! decrease limit length
        for i, cnd in enumerate(df_list, start=0):

            score = 0

            ## MACD VARIABLES
            diff = macd_delta_diff[i]
            idx = sorted_d.index(diff) * (20 / self.limit)

            trend_momentum = 0

            ## ----------------  MACD SCORE IMPLEMENTATION  ----------------
            macd = 0

            if cnd.macd_delta > 0:

                ## MACD bigger than signal,
                ## Generally this case for controlling selling price.
                ## This is proper to selling

                macd = idx - sp if diff > 0 else -(idx + sp)

            else:

                # MACD is smaller than signal Or equal
                # Normally this case is not good to buy.
                # But diff is positive, it is good to buy

                macd = idx + sp if diff >= 0 else -(idx + sp)

            df["macd_score"][i] = macd
            score += macd

            # ## RSI Variables

            rsi_v = df["rsi"][i]
            rsi_diff_v = rsi_diffs[i]

            idx = sorted_rsi_diffs.index(rsi_diff_v) * (10 / self.limit)

            ## ----------------  RSI SCORE IMPLEMENTATION  ----------------

            rs = 0

            if rsi_v > 70:

                rs = idx - sph if rsi_diff_v > 0 else -(15 - idx)

            if 70 >= rsi_v >= 30:

                rs = idx if rsi_diff_v > 0 else (idx + sph - 10)

            if 30 > rsi_v:

                rs = idx + sph if rsi_diff_v >= 0 else (idx + sph - 10)

            trend_momentum += rs
            df["rsi_score"][i] = rs

            ## CCI Variables

            cci_v = df["cci"][i]
            cci_diff_v = cci_diffs[i]

            idx = sorted_cci_diffs.index(cci_diff_v) * (10 / self.limit)

            cci = 0

            if cci_v > 100:
                ## FIX THIS
                cci = idx - 10 - sph
                trend_momentum += cci

            if 100 >= cci_v > 0:

                cci = idx if cci_diff_v > 0 else (idx - 10 - sph)

            if 0 >= cci_v > -100:

                cci = idx + sph if cci_diff_v > 0 else (idx - 10 - sph)

                trend_momentum += cci

            if -100 >= cci_v:

                cci = idx if cci_diff_v > 0 else (idx - 10 - sph)

                trend_momentum += cci

            df["cci_score"][i] = cci

            ## SMA Variables

            sma_10 = df["sma_9"][i]
            sma_20 = df["sma_21"][i]
            price = df["close"][i]
            sma_diff = sma_diffs[i]

            idx = sorted_sma_diffs.index(sma_diff) * (20 / self.limit)

            sma = 0

            if sma_10 > sma_20 and price >= sma_10:

                sma = idx + sp if sma_diff > 0 else idx - (20 + sp)

                score += sma

            if sma_10 > sma_20 and sma_10 > price:
                ## going Down! SELL

                sma = idx if sma_diff > 0 else idx - (20 + sp)

                score += sma

            if sma_10 == sma_20:

                sma = idx if sma_diff > 0 else idx - 20

                score += sma

            if sma_20 > sma_10 and sma_10 > price:
                ## Going Down! SELL

                sma = idx if sma_diff > 0 else idx - (20 + sp)

                score += sma

            if sma_20 > sma_10 and price >= sma_10:

                sma = idx if sma_diff > 0 else idx - 20

                score += sma

                ## Depending on price changes.

            df["sma_score"][i] = sma

            score += trend_momentum

            df["score"][i] = score

        i = len(df.index) - 1

        score = df["score"][i]
        price = df["close"][i]

        # strategie scores
        macd_score = df["macd_score"][i]
        rsi_score = df["rsi_score"][i]
        sma_score = df["sma_score"][i]
        cci_score = df["cci_score"][i]

        # indicators
        rsi = df["rsi"][i]
        sma2 = df["sma_21"][i]
        [ema, ema_pre] = df["ema"][-2:]
        [sma1, sma1_pre] = df["sma_9"][-2:]

        self.last_price = price

        score_diff = df["score"].diff().fillna(0)

        info = f"\n= = = = = = = = = = = = = = = = = = =\n \
            Macd : {macd_score},Rsi : {rsi_score},Cci : {cci_score}, \
            Sma : {sma_score}\nScore : {score} -  Score Diff : {score_diff[i]}\n"

        writeFile(info, "output")

        # * MACD score is important w/ crossing macd & signal line. On Possible going up moment,
        # * we can more times say macd crossing signal line to positive direction

        # * rsi score is important for selling point. So, if we catch any decreasing moment for this indicator.
        # * we should use this opportunity to sell
        # * If Sma-21, crosses Sma-51 on positive direction. It can be going up along approximately 10-20 candles.

        # * rsi > 30 , rsi_score > 0 macd_score > 0 , ema_9 > sma_9 ,( sma_score > 0 can be)  score > 10

        if rsi > 30 and rsi_score > 0 and macd_score > 0:

            # ! If you divide your money into any piece of count. you can decrease your loss risk for "leverage" position.

            # ! sometimes score can be negative
            if ema > sma1 and sma1_pre >= ema and score > 0 and score_diff[i] > 0:
                signal = "BUY"

        if rsi >= 80 and rsi_score <= 0:
            signal = "SELL"

        if (
            sma1 > ema
            and sma1_pre <= ema_pre
            and macd_score < 0
            and score < -10
            and (cci_score < 0 or rsi_score < 0)
        ):
            signal = "SELL"

        if rsi >= 70 and rsi_score <= 0 and macd_score <= 0:

            signal = "SELL"

        self.signal = signal
        self.df = df
