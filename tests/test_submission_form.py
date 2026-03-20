import os
import pandas as pd
import pytest
from pathlib import Path
from benchmark import create_submission_form  # Import your function

# Expected schema
EXPECTED_COLUMNS = [
    "configuration", "cup", "filling (ml)", "grasp type", "handover location", "subject",
    "w^i (mm)", "w^i_b (mm)", "h^i (mm)", "m^i_v (grams)", "f^i (%)",
    "m^i_r (grams)", "d^i (mm)", "w^i (grams)",
    "t^i_{hm} (ms)", "t^i_{ho} (ms)", "t^i_{rm} (ms)"
]

@pytest.fixture
def temp_csv_path(tmp_path: Path):
    """Fixture to provide a temporary CSV path."""
    return tmp_path / "test_submission_form.csv"

def test_dataframe_row_count(temp_csv_path):
    """Ensure the DataFrame has exactly 288 rows."""
    df = create_submission_form(output_path=temp_csv_path)
    assert len(df) == 288, f"Expected 288 rows, got {len(df)}"

def test_dataframe_columns(temp_csv_path):
    """Ensure the DataFrame has the correct columns in the correct order."""
    df = create_submission_form(output_path=temp_csv_path)
    assert list(df.columns) == EXPECTED_COLUMNS, "Column names or order do not match expected schema"

def test_csv_file_creation(temp_csv_path):
    """Ensure the CSV file is created and contains correct data."""
    df = create_submission_form(output_path=temp_csv_path)
    assert temp_csv_path.exists(), "CSV file was not created"
    
    # Read back the CSV and compare
    df_from_csv = pd.read_csv(temp_csv_path)
    assert df_from_csv.equals(df), "CSV file contents do not match the generated DataFrame"
