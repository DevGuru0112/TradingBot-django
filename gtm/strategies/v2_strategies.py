from ..api.binance_api_manager import Binance_API_Manager
from ..data.logger import Logger
from .helper import writeFile
from .analyzers.analyzer import analyze3m



logger = Logger("strategies")


class V2Strategies:
    def __init__(self, binance_manager: Binance_API_Manager, symbol):
        self.client = binance_manager.client
        self.symbol = symbol
        self.limit = 101

    def ch3mGetSignal(self, df):
        
        



        signal = analyze3m(df)

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

            # * If you divide your money into any piece of count. you can decrease your loss risk for "leverage" position.
            # * sometimes score can be negative

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
