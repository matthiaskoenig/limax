import pytest
from limax import EXAMPLE_LIMAX_PATH
from limax.io import convert_limax_csv


def test_convert_limax_io():
    """Test conversion functionality."""
    df = convert_limax_csv(EXAMPLE_LIMAX_PATH)
    assert not df.empty
    assert "time" in df.columns
