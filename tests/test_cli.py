import pytest
import tempfile
import argparse
from pathlib import Path
from corsmal_toolkit.cli import get_parser, existing_file, ensure_csv_exists

def test_existing_file_valid():
    with tempfile.NamedTemporaryFile() as f:
        assert existing_file(f.name) == f.name

def test_existing_file_missing():
    with pytest.raises(argparse.ArgumentTypeError):
        existing_file("/nonexistent/path/file.csv")

def test_ensure_csv_exists_creates_template():
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = f"{tmpdir}/test.csv"
        result = ensure_csv_exists(csv_path)
        assert Path(csv_path).exists()
        assert result == csv_path

def test_get_parser_returns_parser():
    parser = get_parser()
    assert parser is not None
    args = parser.parse_args(["--benchmark", "--submission_csv", "test.csv"])
    assert args.benchmark == True