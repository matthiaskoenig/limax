"""Definition of command line commands for limax."""
import argparse
from pathlib import Path

from limax import __citation__, __version__, log
from limax.console import console
from limax.io import read_limax_dir, read_limax_file


logger = log.get_logger(__name__)


def main() -> None:
    """Entry point which runs LiMAx script.

    The script is registered as `limax` command.

    Example (process single file):
        limax -i src/limax/resources/patient1.csv -o src/limax/resources/limax_example_processed.csv

    Example (process all limax file in folder):
        limax --input_dir src/limax/resources --output_dir src/limax/resources
    """

    import optparse
    import sys

    parser = optparse.OptionParser()
    parser.add_option(
        "-i",
        "--input",
        action="store",
        dest="input_file",
        help="Path to single input LiMAx raw file as '*.csv'.",
    )
    parser.add_option(
        "--input_dir",
        action="store",
        dest="input_dir",
        help="Path to input folder with LiMAx raw files as '*.csv'.",
    )
    parser.add_option(
        "-o",
        "--output_dir",
        action="store",
        dest="output_dir",
        help="Path to output folder with processed LiMAx files as '*.json'.",
    )

    console.rule(style="white")
    console.print(":syringe: LIMAX ANALYSIS :syringe:")
    console.print(f"Version {__version__} (https://github.com/matthiaskoenig/limax)")
    console.print(f"Citation {__citation__}")
    console.rule(style="white")
    console.print("Example single file:")
    console.print("    limax -i patient1.csv -o .")
    console.print("Example folder:")
    console.print("    limax --input_dir limax_examples --o limax_examples_processed")
    console.rule(style="white")

    options, args = parser.parse_args()

    def _parser_message(text: str) -> None:
        console.print(text)
        parser.print_help()
        console.rule(style="white")
        sys.exit(1)

    if not options.input_file and not options.input_dir:
        _parser_message("Required argument '--input_file' or '--input_dir' missing")
    if options.input_file and options.input_dir:
        _parser_message(
            "Provide either argument '--input_file' or '--input_dir', not both"
        )
    if not options.output_dir:
        _parser_message("Required argument '--output_dir' missing")

    output_dir = Path(options.output_dir)

    # process single LiMAx
    if options.input_file:
        input_file = Path(options.input_file)
        if not input_file.exists():
            _parser_message(f"'--input_file {input_file}' does not exist.")
        if not input_file.is_file():
            _parser_message(f"'--input_file {input_file}' is not a file.")
        read_limax_file(limax_csv=input_file, output_dir=output_dir)

    # process folder with LiMAx raw data
    elif options.input_dir and options.output_dir_path:
        input_dir = Path(options.input_dir)

        if not input_dir.exists():
            _parser_message(f"'--input_dir {input_dir}' does not exist.")
        if not input_dir.is_dir():
            _parser_message(f"'--input_dir {input_dir}' is not a directory.")

        # process all files
        read_limax_dir(input_dir=input_dir, output_dir=output_dir)


if __name__ == "__main__":
    main()
