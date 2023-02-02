"""
Reading data from RAW Limax files.

Anonymization.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd

from limax import log
from limax.console import console
from limax.model import LX, LXData, LXMetaData
from limax.plot import plot_lx_matplotlib


logger = log.get_logger(__file__)


def read_limax_dir(input_dir: Path, output_dir: Path) -> None:
    """Read limax data from folder."""
    # process all files
    for limax_csv in input_dir.glob("**/*.csv"):
        limax_csv_rel = limax_csv.relative_to(input_dir)
        output_path: Path = Path(output_dir / limax_csv_rel)
        parse_limax_file(limax_csv=limax_csv, output_dir=output_path.parent)


class MetadataParser:
    """Helper class to parse LiMAx metadata."""

    patient_metadata_fields = [
        "food_abstinence",
        "smoking",
        "oxygen",
        "ventilation",
        "medication",
    ]

    @staticmethod
    def _parse_patient_metadata(
        line: Optional[str], separator: str = ","
    ) -> Dict[str, Union[str, bool]]:
        """Parse patient metadata from metadata line.

        # Nahrungskarenz: über 3 Std., Raucher: Nein, Sauerstoff: Nein, Beatmung: Nein, Medikation: Ja
        """
        if not line:
            return {
                "food_abstinence": "-",
                "smoking": False,
                "oxygen": False,
                "ventilation": False,
                "medication": False,
            }
        else:
            tokens = line.split(separator)
            d: Dict[str, str] = {}
            for k, key in enumerate(MetadataParser.patient_metadata_fields):
                try:
                    d[key] = tokens[k].split(":")[1].strip()
                except IndexError:
                    logger.error(f"'{key}' could not be parsed from '{tokens[k]}'")
                    d[key] = "-"

            d_processed: Dict[str, Union[str, bool]] = {**d}
            for key in ["smoking", "oxygen", "ventilation", "medication"]:
                if d[key].lower() == "ja":
                    d_processed[key] = True
                elif d[key].lower() == "nein":
                    d_processed[key] = False
                else:
                    logger.error(f"Invalid value in metadata: '{key}: {d[key]}'")
                    d_processed[key] = False

            if d["food_abstinence"] == "über 3 Std.":
                d_processed["food_abstinence"] = "> 3 hr"
            return d_processed

    @staticmethod
    def _parse_mid(line: str) -> str:
        """Parse mid."""
        mid = "-"
        try:
            mid = line.split()[1]
        except (IndexError, ValueError) as err:
            logger.error(f"'mid' could not be parsed from '{line}'. {err}")
        return mid

    @staticmethod
    def parse_datetime(line: str) -> str:
        """Parse datetime information.

        Example: 01.01.2010 08:30
        """
        date_str = line
        try:
            # Check that date can be parsed
            date = datetime.strptime(line, "%d.%m.%Y %H:%M")
            date_str = date.strftime("%Y-%m-%d %H:%M")

        except ValueError:
            logger.error(
                f"'datetime' could not be parsed in format '%d.%m.%Y %H:%M' from '{line}"
            )

        return date_str

    @staticmethod
    def parse_sex(line: str) -> str:
        """Parse sex in {M, F, NA}."""
        if line == "männlich":
            return "M"
        elif line == "weiblich":
            return "F"
        else:
            logger.error(f"'sex' could not be parsed from '{line}'")
            return "NA"

    @staticmethod
    def parse_height(line: str) -> float:
        """Parse patient height in [cm]."""
        height: float = -1.0
        try:
            tokens = line.split()
            height = float(tokens[0])
            if tokens[1] != "cm":
                logger.error(f"'height' unit is not cm, but '{tokens[1]}'")
        except (IndexError, ValueError) as err:
            logger.error(f"'height' could not be parsed from '{line}'. {err}")
        return height

    @staticmethod
    def parse_weight(line: str) -> float:
        """Parse patient weight in [kg]."""
        height: float = -1.0
        try:
            tokens = line.split()
            height = float(tokens[0])
            if tokens[1] != "kg":
                logger.error(f"'weight' unit is not kg, but '{tokens[1]}'")
        except (IndexError, ValueError) as err:
            logger.error(f"'weight' could not be parsed from '{line}'. {err}")
        return height

    @staticmethod
    def parse_value(line: str) -> float:
        """Parse value field."""
        value: float = -1.0
        try:
            line = line.replace(",", ".").strip()
            value = float(line)
        except (IndexError, ValueError) as err:
            logger.error(f"'value' could not be parsed. {err}")
        return value

    @classmethod
    def parse(cls, md_lines: List[str]) -> LXMetaData:
        """Parse metadata from metadata lines."""
        mid = cls._parse_mid(md_lines[0]),
        datetime = cls.parse_datetime(md_lines[3])

        # max integer
        k_pmd: int: np.
        line_pmd: Optional[str] = None
        line_weight: Optional[str] = None
        line_height: Optional[str] = None
        line_sex: Optional[str] = None
        lines_value: List[str] = []
        lines_comment: List[str] = []  # all the lines after Nahrungskarenz
        for k, line in enumerate(md_lines):


            if line.startswith("Nahrungskarenz"):
                line_pmd = line
            elif line.endswith(" cm"):
                line_height = line
            elif line.weight(" cm"):
                line_height = line

        pmd_dict = cls._parse_patient_metadata(line_pmd)

        md_dict: Dict[str, Any]
        if len(md_lines) == 11:
            """
            Format 1 (length=11):

            # mID 102
            # 'doc' (, )
            # Dr. Max Mustermann
            # 01.01.2010 08:30
            # utouARg
            # 160 cm
            # 70 kg
            # 43,295187
            # 44,395187
            # 630,0
            # Nahrungskarenz: über 3 Std., Raucher: Nein, Sauerstoff: Nein, Beatmung: Nein, Medikation: Ja
            """
            md_dict = {
                "mid": cls._parse_mid(md_lines[0]),
                "datetime": cls.parse_datetime(md_lines[3]),
                "sex": "NA",
                "height": cls.parse_height(md_lines[5]),
                "weight": cls.parse_weight(md_lines[6]),
                "value1": cls.parse_value(md_lines[7]),
                "value2": cls.parse_value(md_lines[8]),
                **cls._parse_patient_metadata(md_lines[10]),
            }

        elif len(md_lines) > 11:
            """
            Format 2 (length=14):

            # mID 805
            # 'doc' (, )
            # Dr. Falk Rauchfuß
            # 24.12.2021 12:24
            # Max Mustermann
            # 24.12.1999
            #
            # weiblich
            # 162 cm
            # 54 kg
            # 31,762406
            # 513,0
            #
            # Nahrungskarenz: über 3 Std., Raucher: Nein, Sauerstoff: Nein, Beatmung: Nein, Medikation: Ja
            #
            # Wir berichten Ihnen über die durchgeführten Untersuchungen bei unserem gemeinsamen Patienten / unserer gemeinsamen Patientin:
            # Der LiMAx-Test gibt die aktuelle Leberfunktionskapazität des CYP1A2-Systems an. Aktuell ist dieser Wert ...
            """
            md_dict = {
                "mid": cls._parse_mid(md_lines[0]),
                "datetime": cls.parse_datetime(md_lines[3]),
                "sex": cls.parse_sex(md_lines[6]),
                "height": cls.parse_height(md_lines[7]),
                "weight": cls.parse_weight(md_lines[8]),
                "value1": cls.parse_value(md_lines[9]),
                "value2": cls.parse_value(md_lines[10]),
                **cls._parse_patient_metadata(md_lines[11]),
            }

        else:
            raise ValueError(
                "Unsupported LiMAx MetaData format. Please send the LiMAx "
                "file for debugging."
            )

        lx_metadata: LXMetaData = LXMetaData(**md_dict)
        return lx_metadata


def parse_limax_file(
    limax_csv: Path,
    output_dir: Optional[Path] = None,
) -> LX:
    """Read limax data."""
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        # limax_path = output_dir / f"{limax_csv.stem}.txt"
        json_path = output_dir / f"{limax_csv.stem}.json"
        fig_path = output_dir / f"{limax_csv.stem}.png"
        console.print()
        console.rule(
            title=f"[bold white]Process '{limax_csv}'", align="left", style="[white]"
        )

    # parse file
    line_offset = -1
    lines: List[str] = []

    with open(limax_csv, "r") as f:
        raw_lines: List[str] = f.readlines()

        # cleanup lines
        for line in raw_lines:
            # remove comment character
            if line.startswith("# "):
                line = line[2:]
            # strip whitespace
            line = line.strip()
            # remove empty lines
            if len(line) > 0:
                lines.append(line)

        # find metadata offset in clean lines
        for k, line in enumerate(lines):
            if line.startswith("Zeit"):
                line_offset = k
                break
        else:
            raise ValueError(
                f"No line starting with 'Zeit' in csv, invalid LIMAX file: {limax_csv}"
            )

    md_lines = lines[:line_offset]
    data_lines = lines[line_offset + 1 :]

    # parse metadata
    lx_metadata: LXMetaData = MetadataParser.parse(md_lines)

    # parse data
    time, dob, error = [], [], []
    for line in data_lines:
        # cleanup of lines
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

    # sort by time (some strange artefacts in some files)
    df.sort_values(by=["time"], inplace=True)
    lx_data = LXData(
        time=list(df.time.values), dob=list(df.dob.values), error=list(df.error.values)
    )
    lx = LX(metadata=lx_metadata, data=lx_data)
    console.print(lx_metadata)

    # serialization to JSON
    if output_dir:
        with open(json_path, "w") as f_json:
            f_json.write(lx.json(indent=2))
        plot_lx_matplotlib(lx, fig_path=fig_path)

    return lx


if __name__ == "__main__":
    from limax import (
        EXAMPLE_LIMAX_PATIENT1_PATH,
        EXAMPLE_LIMAX_PATIENT2_PATH,
        EXAMPLE_LIMAX_PATIENT3_PATH,
        EXAMPLE_LIMAX_PATIENT2017_PATH,
        EXAMPLE_LIMAX_PATIENT2018_PATH,
        EXAMPLE_LIMAX_PATIENT2022_PATH,
        PROCESSED_DIR,
    )

    for path in [
        # EXAMPLE_LIMAX_PATIENT1_PATH,
        # EXAMPLE_LIMAX_PATIENT2_PATH,
        # EXAMPLE_LIMAX_PATIENT3_PATH,
        # EXAMPLE_LIMAX_PATIENT2017_PATH,
        EXAMPLE_LIMAX_PATIENT2018_PATH,
        # EXAMPLE_LIMAX_PATIENT2022_PATH,
    ]:
        lx = parse_limax_file(limax_csv=path, output_dir=PROCESSED_DIR)
        # console.print(lx)
        # console.print(lx.json())
        console.print()
        console.print(lx.data.to_df().head(5))

    # read_limax_dir(input_dir=RAW_DIR, output_dir=PROCESSED_DIR)
