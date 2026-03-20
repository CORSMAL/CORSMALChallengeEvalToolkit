import os
import pandas as pd
import pytest
from pathlib import Path

from corsmal_toolkit.submission_form import create_submission_form 

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

def test_data_patterns(temp_csv_path):
    """Validate that the generated data follows the expected repeating patterns."""
    df = create_submission_form(output_path=temp_csv_path)

    # 1. Cup pattern
    expected_cups = ([1] * 18 + [2] * 18 + [3] * 18 + [4] * 18) * 4
    assert df["cup"].tolist() == expected_cups, "Cup pattern does not match expected sequence"

    # 2. Filling pattern
    expected_filling = []
    for val in [0, 125, 0, 400, 0, 450, 0, 300]:
        expected_filling.extend([val] * 9)
    expected_filling *= 4
    assert df["filling (ml)"].tolist() == expected_filling, "Filling pattern does not match expected sequence"

    # 3. Grasp type pattern
    expected_grasp = ([1] * 3 + [2] * 3 + [3] * 3) * 32
    assert df["grasp type"].tolist() == expected_grasp, "Grasp type pattern does not match expected sequence"

    # 4. Handover location pattern
    expected_handover = [1, 2, 3] * 96
    assert df["handover location"].tolist() == expected_handover, "Handover location pattern does not match expected sequence"

    # 5. Subject pattern
    expected_subjects = [1] * 72 + [2] * 72 + [3] * 72 + [4] * 72
    assert df["subject"].tolist() == expected_subjects, "Subject pattern does not match expected sequence"

def test_numeric_columns_initialized_to_minus_one(temp_csv_path):
    """Ensure all measurement columns are initialized to -1."""
    df = create_submission_form(output_path=temp_csv_path)

    # Columns that must be initialized to -1
    measurement_columns = [
        "w^i (mm)", "w^i_b (mm)", "h^i (mm)", "m^i_v (grams)", "f^i (%)",
        "m^i_r (grams)", "d^i (mm)", "w^i (grams)",
        "t^i_{hm} (ms)", "t^i_{ho} (ms)", "t^i_{rm} (ms)"
    ]

    for col in measurement_columns:
        assert all(df[col] == -1), f"Column '{col}' is not fully initialized to -1"
