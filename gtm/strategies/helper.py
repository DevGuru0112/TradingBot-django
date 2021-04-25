import os


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


def writeFile(text):

    filename = "output.txt"

    if os.path.exists(filename):
        append_write = "a"  # append if already exists
    else:
        append_write = "w"  # make a new file if not

    f = open(filename, append_write)
    f.write(text)
    f.close()
