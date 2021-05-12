from ..data.logger import Logger

import pandas as pd
import os


logger = Logger("trader")

output_dir = "output/"


def strArrToIntArr_2d(s_arr: list):

    # This function convert 2d str array to 2d int array

    ml = []
    for sl in s_arr:
        l = []

        for si in sl:

            if type(si) is str:

                l.append(float(si) if "." in si else int(si))

            else:
                l.append(si)

        ml.append(l)

    return ml


def writeFile(text, filename):

    filename = output_dir + filename + ".txt"

    if os.path.exists(filename):
        append_write = "a"  # append if already exists
    else:
        append_write = "w"  # make a new file if not

    f = open(filename, append_write)

    f.write(text)

    f.close()


def writeExcel(df : pd.DataFrame):    
    # create excel writer


    writer = pd.ExcelWriter('output/output.xlsx')
    # write dataframe to excel sheet named 'marks'
    df.to_excel(writer, 'trade')
    # save the excel file
    writer.save()
    print('DataFrame is written successfully to Excel Sheet.')