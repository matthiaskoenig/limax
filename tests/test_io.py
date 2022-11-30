"""Test LiMAx IO functionality."""
from pathlib import Path

from limax import EXAMPLE_LIMAX_PATH
from limax.io import read_limax_file


def test_convert_limax_io(tmp_path: Path) -> None:
    """Test conversion functionality."""
    output_path: Path = tmp_path / "output.csv"
    lx = read_limax_file(limax_csv=EXAMPLE_LIMAX_PATH, output_dir=output_path)
    assert lx
    df = lx.data.to_df()
    assert not df.empty
    assert "time" in df.columns
    assert output_path.exists()


def test_json_serialization(tmp_path: Path) -> None:
    """Test roundtrip to JSON."""
    lx = read_limax_file(limax_csv=EXAMPLE_LIMAX_PATH, output_dir=output_path)
