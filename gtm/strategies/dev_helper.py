import pandas as pd

output_dir = "output/"


def write_excel(df: pd.DataFrame, filename, sheet_name):

    path = output_dir + filename + ".csv"

    df.to_csv(path, index=True)
