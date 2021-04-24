import pandas as pd
from datetime import datetime
from ..helper import strArrToIntArr_2d

class AnalyzerUtils():
    
    def convert_to_dataframe(self,hd):
        """ Convert historical data matrix to a pandas dataframe

        @args => historical_data (List) : a matrix of historical OHCLV data

        @return => pandas.DataFrame : Contains the historical data in a pandas dataFrame

        """

        hd = strArrToIntArr_2d(hd)

        df = pd.DataFrame(hd)

        df.transpose()


        df.columns = ["timestamp","open","high","low","close","volume","closetimeStamp","quote_asset_volume","number_of_trades","tbb_asset_volume","tbq_asset_volume","ignored"]

        df["datetime"] = df.timestamp.apply(
            lambda x: pd.to_datetime(datetime.fromtimestamp(x / 1000).strftime('%c'))
        )

        df.set_index("datetime",inplace=True,drop=True)
        df.drop("timestamp",axis=1,inplace=True)



        return df
