from ..trader.binance_api_manager import Binance_API_Manager
from binance.exceptions import BinanceAPIException, BinanceRequestException
from datetime import datetime
from .analyzers.indicators import Indicators
from ..data.logger import Logger
from binance.client import Client
from .dev_helper import write_excel

import pandas as pd

logger = Logger("strategies")


class V1Strategies:
    def __init__(self, binance_manager: Binance_API_Manager, symbol):
        self.client = binance_manager.client
        self.symbol = symbol
        self.limit = 101

    def ch3mGetSignal(self):

        sp = 5
        sph = sp / 2

        # GENERATE SEQUENTLY CHAIN MODEL (THINK ABOUT IT)

        # example: first RSI and CCI controlling and generating a score for depending on movement
        # after that MACD Controlling and generating a score depending on movement with RSI/CCI score !!!

        # TODO #1 => calculate all of 3m row changes. And calculate how much increase klines
        # TODO #1 => and how much decrease klines which is determined on interval.
        # TODO #1 => calculate all of increased klines average. Example 0.25% increase is average of all increased klines.
        # TODO #1 => if current increase value is bigger than average. It is possible going up

        candles = None

        try:
            # If goes something wrong! return none
            candles = self.client.get_klines(
                symbol=self.symbol,
                interval=Client.KLINE_INTERVAL_3MINUTE,
                limit=self.limit,
            )

        except (BinanceAPIException, BinanceRequestException) as e:
            
            traceback.print_exception(type(e), e, e.__traceback__)
            logger.error(e)

            return pd.DataFrame()

        indicators = Indicators(self.symbol, candles)

        self.df = indicators.calculate()

        df_list = self.df.itertuples(index=True)

        ## MACD Variables

        macd_delta_diff = self.df["macd_delta"].diff().fillna(0)

        sorted_d = macd_delta_diff.sort_values().tolist()

        ## RSI Variables

        rsi_diffs = self.df["rsi"].diff().fillna(0)
        sorted_rsi_diffs = rsi_diffs.sort_values().tolist()

        ## CCI Variables

        cci_diffs = self.df["cci"].diff().fillna(0)
        sorted_cci_diffs = cci_diffs.sort_values().tolist()

        ## SMA Variables

        # delta_sma = self.df["sma_21"] - self.df["sma_51"]

        sma_diffs = self.df["sma_21"].diff().fillna(0)

        sorted_sma_diffs = sma_diffs.sort_values().tolist()

        self.df["score"] = 0
        self.df["sma_score"] = 0
        self.df["rsi_score"] = 0
        self.df["cci_score"] = 0
        self.df["macd_score"] = 0

        for i, cnd in enumerate(df_list, start=0):

            score = 0

            ## MACD VARIABLES
            diff = macd_delta_diff[i]
            idx = sorted_d.index(diff) * (20 / self.limit)

            trend_momentum = 0

            ## ----------------  MACD SCORE IMPLEMENTATION  ----------------

            if cnd.macd_delta > 0:

                ## MACD bigger than signal,
                ## Generally this case for controlling selling price.
                ## This is proper to selling

                macd = idx - sp if diff > 0 else -(idx + sp)
                score += macd

                self.df["macd_score"][i] = macd

            else:

                # MACD is smaller than signal Or equal
                # Normally this case is not good to buy.
                # But diff is positive, it is good to buy

                macd = idx + sp if diff >= 0 else -(idx + sp)

                score += macd

                self.df["macd_score"][i] = macd

            # ## RSI Variables

            rsi_v = self.df["rsi"][i]
            rsi_diff_v = rsi_diffs[i]

            idx = sorted_rsi_diffs.index(rsi_diff_v) * (10 / self.limit)

            ## ----------------  RSI SCORE IMPLEMENTATION  ----------------

            if rsi_v > 70:

                rs = idx - sph if rsi_diff_v > 0 else -(15 - idx)

                trend_momentum += rs

                self.df["rsi_score"][i] = rs

            if 70 >= rsi_v >= 30:

                rs = idx if rsi_diff_v > 0 else (idx + sph - 10)

                trend_momentum += rs

                self.df["rsi_score"][i] = rs

            if 30 > rsi_v:

                rs = idx + sph if rsi_diff_v >= 0 else (idx + sph - 10)

                trend_momentum += rs

                self.df["rsi_score"][i] = rs

            ## CCI Variables

            cci_v = self.df["cci"][i]
            cci_diff_v = cci_diffs[i]

            idx = sorted_cci_diffs.index(cci_diff_v) * (10 / self.limit)

            if cci_v > 100:
                ## FIX THIS
                cci = idx - 10 - sph
                trend_momentum += cci

                self.df["cci_score"][i] = cci

            if 100 >= cci_v > 0:

                cci = idx if cci_diff_v > 0 else (idx - 10 - sph)

                trend_momentum += cci

                self.df["cci_score"][i] = cci
            if 0 >= cci_v > -100:

                cci = idx + sph if cci_diff_v > 0 else (idx - 10 - sph)

                trend_momentum += cci

                self.df["cci_score"][i] = cci

            if -100 >= cci_v:

                cci = idx if cci_diff_v > 0 else (idx - 10 - sph)

                trend_momentum += cci

                self.df["cci_score"][i] = cci

            ## SMA Variables

            sma_21 = self.df["sma_21"][i]
            sma_51 = self.df["sma_51"][i]
            price = self.df["close"][i]
            sma_diff = sma_diffs[i]

            idx = sorted_sma_diffs.index(sma_diff) * (20 / self.limit)

            if sma_21 > sma_51 and price >= sma_21:

                sma = idx + sp if trend_momentum > 0 else idx - (20 + sp)

                score += sma

                self.df["sma_score"][i] = sma

            if sma_21 > sma_51 and sma_21 > price:
                ## going Down! SELL

                sma = idx if trend_momentum > 0 else idx - (20 + sp)

                score += sma

                self.df["sma_score"][i] = sma

            if sma_21 == sma_51:

                sma = idx if trend_momentum > 0 else idx - 20

                score += sma

                self.df["sma_score"][i] = sma

            if sma_51 > sma_21 and sma_21 > price:
                ## Going Down! SELL

                sma = idx if trend_momentum > 0 else idx - (20 + sp)

                score += sma

                self.df["sma_score"][i] = sma

            if sma_51 > sma_21 and price >= sma_21:

                sma = idx if trend_momentum > 0 else idx - 20

                score += sma

                self.df["sma_score"][i] = sma

                ## Depending on price changes.

            score += trend_momentum

            self.df["score"][i] = score

        #write_excel(self.df, "gtm_score", "gtm")
        return self.df
