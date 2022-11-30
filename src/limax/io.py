"""
Reading data from RAW Limax files.

Anonymization.
"""

from pydantic import BaseModel
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
from pymetadata.log import console


class MetaData(BaseModel):
    """LiMAx metadata.

    0 # mID 102
    1 # 'doc' (, )
    2 # Dr. Max Mustermann
    3 # 01.01.2010 08:30
    4 # utouARg
    5 # 160 cm
    6 # 70 kg
    7 # 43,295187
    8 # 44,395187
    9 # 630,0
    10 # Nahrungskarenz: über 3 Std., Raucher: Nein, Sauerstoff: Nein, Beatmung: Nein, Medikation: Ja
    """

    mid: str
    name: str
    datetime: str
    height: float
    weight: float
    smoking: bool
    oxygen: bool
    ventilation: bool
    medication: bool
    food_abstinence: str


class Limax(BaseModel):
    """LiMAx DOB curve."""

    metadata: MetaData
    data: pd.DataFrame

    class Config:
        """Config for DOB curve."""
        arbitrary_types_allowed = True


def read_limax_dir(input_dir: Path, output_dir: Path) -> None:
    """Read limax data from folder."""
    # process all files
    for limax_csv in input_dir.glob("**/*.csv"):
        limax_csv_rel = limax_csv.relative_to(input_dir)
        output_path: Path = Path(output_dir / limax_csv_rel)
        read_limax_file(limax_csv=limax_csv, output_path=output_path)


def read_limax_file(
    limax_csv: Path, output_path: Path, line_offset: int = 13
) -> Limax:
    """Read limax data."""
    console.log(f"Processing '{limax_csv}' -> '{output_path}'")
    with open(limax_csv, "r") as f:
        lines: List[str] = f.readlines()
        # remove empty lines
        lines = [line.strip() for line in lines]
        lines = [line for line in lines if len(line) > 0]
        # strip header lines
        time, dob, error = [], [], []

        # parse metadata
        md_lines = lines[:line_offset]
        metadata_dict: Dict[str, Any] = {
            "mid": ,
            "name": md_lines[],
            "datetime": "str",
            "height": "float",
            "weight": "float",
            "smoking": "bool",
            "oxygen": "bool",
            "ventilation": "bool",
            "medication": "bool",
            "food_abstinence": "str",
        }
        metadata: MetaData = MetaData(**metadata_dict)

        # parse data
        for line in lines[line_offset:]:
            tokens = [t.strip() for t in line.split("\t")]
            time.append(int(tokens[0]))
            dob.append(float(tokens[1]))
            error.append(str(tokens[2]))

    d: Dict[str, Any] = {
        "time": time,
        "dob": dob,
        "error": error,
    }
    df = pd.DataFrame(data=d)
    df = df[["time", "dob", "error"]]
    # make columns numeric
    # df = pd.to_numeric(df)
    # print(df.head())

    # sort by time (some strange artefacts in some files)
    df.sort_values(by=["time"], inplace=True)
    df.to_csv(output_path, sep="\t", index=False)

    return Limax(metadata=metadata, data=df)


if __name__ == "__main__":
    from limax import EXAMPLE_LIMAX_PATH, PROCESSED_DIR, RAW_DIR

    df = read_limax_file(
        limax_csv=EXAMPLE_LIMAX_PATH,
        output_path=PROCESSED_DIR / EXAMPLE_LIMAX_PATH.name,
    )
    print(df)

    # read_limax_dir(input_dir=RAW_DIR, output_dir=PROCESSED_DIR)
