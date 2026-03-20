#!/usr/bin/env python
# Evaluation script for the CORSMAL Benchmark
# Refer to: https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=8968407
#
################################################################################## 
# Authors: 
# - Alessio Xompero
# - Xavier Weber
# 
#
#  Created Date: 2026/03/20
# Modified Date: 2026/03/20
################################################################################## 

import pandas as pd

from loguru import logger

def create_submission_form(output_path: str = "./submission_form.csv") -> pd.DataFrame:
    """
    Create a structured submission form DataFrame for CORSMAL evaluation.

    Args:
        output_path (str): Path to save the generated CSV file.

    Returns:
        pd.DataFrame: The generated submission form.
    """
    # Constants
    NUM_CONFIGS = 288
    CUP_TYPES = [1, 2, 3, 4]
    FILLING_VALUES = [0, 125, 0, 400, 0, 450, 0, 300]
    GRASP_TYPES = [1, 2, 3]
    HANDOVER_LOCATIONS = [1, 2, 3]
    SUBJECTS = [1, 2, 3, 4]

    # Generate repeated patterns
    cups = ( [cup] * 18 for cup in CUP_TYPES )
    cups = list(sum(cups, [])) * 4

    filling_ml = []
    for val in FILLING_VALUES:
        filling_ml.extend([val] * 9)
    filling_ml *= 4

    grasp_types = (GRASP_TYPES * 3) * 32
    handover_location = HANDOVER_LOCATIONS * 96
    subjects = sum(([sub] * 72 for sub in SUBJECTS), [])

    # Create DataFrame
    df = pd.DataFrame({
        "configuration": list(range(1, NUM_CONFIGS + 1)),
        "cup": cups,
        "filling (ml)": filling_ml,
        "grasp type": grasp_types,
        "handover location": handover_location,
        "subject": subjects,
        "w^i (mm)": [-1] * NUM_CONFIGS,
        "w^i_b (mm)": [-1] * NUM_CONFIGS,
        "h^i (mm)": [-1] * NUM_CONFIGS,
        "m^i_v (grams)": [-1] * NUM_CONFIGS,
        "f^i (%)": [-1] * NUM_CONFIGS,
        "m^i_r (grams)": [-1] * NUM_CONFIGS,
        "d^i (mm)": [-1] * NUM_CONFIGS,
        "w^i (grams)": [-1] * NUM_CONFIGS,
        "t^i_{hm} (ms)": [-1] * NUM_CONFIGS,
        "t^i_{ho} (ms)": [-1] * NUM_CONFIGS,
        "t^i_{rm} (ms)": [-1] * NUM_CONFIGS
    })

    # Save to CSV with error handling
    try:
        df.to_csv(output_path, index=False)
        logger.info(f"Submission form saved to: {output_path}")
    except OSError as e:
        logger.error(f"Failed to save submission form: {e}")
        raise

    return df