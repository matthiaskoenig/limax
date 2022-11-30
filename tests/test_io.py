"""Test LiMAx IO functionality."""
from pathlib import Path

from limax import EXAMPLE_LIMAX_PATH
from limax.io import read_limax_file


def test_convert_limax_io(tmp_path: Path) -> None:
    """Test conversion functionality."""
    output_path: Path = tmp_path / "output.csv"
    df = read_limax_file(limax_csv=EXAMPLE_LIMAX_PATH, output_path=output_path)
    assert not df.empty
    assert "time" in df.columns
    assert output_path.exists()
