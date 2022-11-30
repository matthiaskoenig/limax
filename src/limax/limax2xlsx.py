"""
Helper script to convert LiMAx.
"""
from pathlib import Path
from typing import List

import pandas as pd


def convert_limax_csv(path_in, path_out):
    with open(path_in, "r") as f:
        lines = f.readlines()
        # remove empty lines
        lines = [line.strip() for line in lines]
        lines = [line for line in lines if len(line)>0]
        # strip header lines
        data = lines[13:]
        time, dob, error = [], [], []
        for k, line in enumerate(data):
            tokens = [t.strip() for t in line.split("\t")]
            time.append(int(tokens[0]))
            dob.append(float(tokens[1]))
            error.append(str(tokens[2]))

    data = {
        'time': time,
        'dob': dob,
        'error': error,
    }
    df = pd.DataFrame(data=data)
    df = df[["time", "dob", "error"]]
    # make columns numeric
    # df = pd.to_numeric(df)
    # print(df.head())

    # sort by time (some strange artefacts in some files)
    df = df.sort_values(by=['time'])

    df.to_csv(path_out, sep="\t", index=False)


if __name__ == "__main__":
    from limax import RESOURCES_DIR, EXAMPLE_LIMAX_PATH
        convert_limax_csv(EXAMPLE_LIMAX_PATH)
