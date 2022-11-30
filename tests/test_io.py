"""Test LiMAx IO functionality."""

import pytest

from limax import EXAMPLE_LIMAX_PATH
from limax.io import read_limax_csv


def test_convert_limax_io() -> None:
    """Test conversion functionality."""
    df = read_limax_csv(EXAMPLE_LIMAX_PATH)
    assert not df.empty
    assert "time" in df.columns
