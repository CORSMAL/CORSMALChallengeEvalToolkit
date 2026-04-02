#!/usr/bin/env python
#
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
# Modified Date: 2026/03/24
################################################################################## 

import os
import sys
import json
import argparse
from pathlib import Path
 
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional

from loguru import logger

# Configure logger
logger.remove()  # Remove default handler
logger.add(sys.stderr, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                              "<level>{level: <8}</level> | "
                              "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                              "<level>{message}</level>",
           level="DEBUG")

# ============================================================================
# Validation Functions
# ============================================================================
 
def existing_file(path: str) -> str:
    """
    Validate that the given path points to an existing file.
    Raises argparse.ArgumentTypeError if not found.
    """
    if not os.path.isfile(path):
        raise argparse.ArgumentTypeError(f"File not found: {path}")
    return path
 
 
def validate_csv_columns(df: pd.DataFrame, required_columns: list, file_type: str = "predictions") -> None:
    """
    Validate that a DataFrame contains all required columns.
    
    Args:
        df: DataFrame to validate
        required_columns: List of column names that must exist
        file_type: Description of the file type for error messages
        
    Raises:
        ValueError: If required columns are missing
    """
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(
            f"Missing required {file_type} columns: {missing_cols}\n"
            f"Available columns: {list(df.columns)}"
        )
    logger.info(f"✓ {file_type.capitalize()} CSV validation passed")
 
 
def validate_prediction_csv(csv_path: str) -> pd.DataFrame:
    """
    Load and validate prediction CSV format.
    
    Args:
        csv_path: Path to the prediction CSV file
    
    Returns:
        pd.DataFrame: Validated prediction dataframe
        
    Raises:
        ValueError: If validation fails
    """
    try:
        df = pd.read_csv(csv_path)
        logger.info(f"Loaded predictions from: {csv_path}")
        logger.debug(f"Shape: {df.shape}, Columns: {list(df.columns)}")
        
        # Required columns based on benchmark_evaluator.py
        # required_columns = [
        #     "w^i (mm)", "w^i_b (mm)", "h^i (mm)",
        #     "m^i_v (grams)", "f^i (%)"
        # ]
        required_columns = [
            "config_id", "robot_initial_pose_x", "robot_initial_pose_y", "robot_initial_pose_z", 
            "robot_initial_pose_q1", "robot_initial_pose_q2", "robot_initial_pose_q3", 
            "robot_initial_pose_q4", "initial_mass_measured_g", "width_top_est_mm_vision", 
            "width_bottom_est_mm_vision", "height_est_mm_vision", "geometry_est_timepoint",
            "mass_full_est_g_vision", "mass_full_est_vision_timepoint", "fill_level_est_percent_vision",
            "fill_level_vision_timepoint", "spill_observed_during_human_maneuvering", 
            "robot_mass_est_available", "robot_mass_est_g", "robot_mass_est_timepoint", 
            "delivery_location_est_x_mm", "delivery_location_est_y_mm", "delivery_location_est_z_mm",
            "final_mass_null_flag", "final_mass_measured_g", "t_human_first_contact_ms", 
            "t_human_last_contact_ms", "t_robot_first_contact_ms", "t_robot_last_contact_ms"
        ]
        validate_csv_columns(df, required_columns, "prediction")
        return df
        
    except pd.errors.ParserError as e:
        raise ValueError(f"Failed to parse prediction CSV: {e}")
    except Exception as e:
        raise ValueError(f"Error loading prediction CSV: {e}")
 
 
def validate_ground_truth_csv(csv_path: str) -> pd.DataFrame:
    """
    Load and validate ground truth CSV format.
    
    Args:
        csv_path: Path to the ground truth CSV file
    
    Returns:
        pd.DataFrame: Validated ground truth dataframe
        
    Raises:
        ValueError: If validation fails
    """
    try:
        df = pd.read_csv(csv_path)
        logger.info(f"Loaded ground truth from: {csv_path}")
        logger.debug(f"Shape: {df.shape}, Columns: {list(df.columns)}")
        
        # Example required columns - adjust based on actual ground truth format
        required_columns = [
            "config_id", "mass", "width_top", "width_bottom", "height",
            "volume", "filling_amount_ml", "filling_amount_g", "total_mass", "fullness"
        ]
        validate_csv_columns(df, required_columns, "ground truth")
        return df
        
    except pd.errors.ParserError as e:
        raise ValueError(f"Failed to parse ground truth CSV: {e}")
    except Exception as e:
        raise ValueError(f"Error loading ground truth CSV: {e}")

def load_configs(csv_path: str) -> pd.DataFrame:
    """
    Load and validate benchmark configurations CSV format.
    
    Args:
        csv_path: Path to the benchmark configurations CSV file
    
    Returns:
        pd.DataFrame: Dataframe with benchmark configurations
        
    Raises:
        ValueError: If validation fails
    """
    try:
        df = pd.read_csv(csv_path)
        logger.info(f"Loaded benchmark configuration from: {csv_path}")
        logger.debug(f"Shape: {df.shape}, Columns: {list(df.columns)}")

        return df

    except pd.errors.ParserError as e:
        raise ValueError(f"Failed to parse benchmark configuration CSV: {e}")
    except Exception as e:
        raise ValueError(f"Error loading benchmark configuration  CSV: {e}")


def _add_error(errors: List[str], msg: str):
    errors.append(msg)

def _add_warning(warnings: List[str], msg: str):
    warnings.append(msg)

def validate_metadata_json(json_path: str) -> Dict[str, Any]:
    """
    Validate a submission metadata JSON file.

    Returns a dict:
      {
        "valid": bool,
        "errors": [ ... ],
        "warnings": [ ... ],
        "summary": { ... }  # key extracted values for quick inspection
      }

    Checks performed (not exhaustive):
      - JSON loads correctly
      - Required top-level sections exist
      - Types for common fields (ints, bools, lists, dicts)
      - Consistency checks:
          * participants.num_human_subjects == len(participants.subject_ids)
          * each subject id present in demographics keys
          * configuration_file.num_configurations == execution_policy.num_configurations
          * table_dimensions_mm is length 3 and numeric
          * video_fps is positive integer
          * execution_policy.runs_per_configuration positive integer
          * physical_assumptions.density_rice_g_per_ml is numeric and within plausible range
      - Flags empty-but-present strings for fields that are likely required
    """
    errors: List[str] = []
    warnings: List[str] = []
    summary: Dict[str, Any] = {}

    # Load JSON
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
    except Exception as e:
        return {"valid": False, "errors": [f"Failed to load JSON: {e}"], "warnings": [], "summary": {}}

    # Top-level keys expected
    expected_top_keys = [
        "submission_version", "submission_timestamp", "protocol_version", "team",
        "ethics", "participants", "hardware", "environment",
        "software_and_models", "annotation_protocol", "configuration_file",
        "physical_assumptions", "learning_policy", "execution_policy"
    ]
    for k in expected_top_keys:
        if k not in metadata:
            _add_error(errors, f"Missing top-level key: '{k}'")

    # Quick summary extraction (if present)
    summary["submission_version"] = metadata.get("submission_version")
    summary["protocol_version"] = metadata.get("protocol_version")
    summary["num_human_subjects"] = None
    if "participants" in metadata and isinstance(metadata["participants"], dict):
        summary["num_human_subjects"] = metadata["participants"].get("num_human_subjects")

    # Validate participants block
    participants = metadata.get("participants")
    if not isinstance(participants, dict):
        _add_error(errors, "participants must be an object/dictionary")
    else:
        nh = participants.get("num_human_subjects")
        ids = participants.get("subject_ids")
        demographics = participants.get("demographics")

        # num_human_subjects
        if nh is None:
            _add_error(errors, "participants.num_human_subjects is missing")
        else:
            if not isinstance(nh, int):
                _add_error(errors, "participants.num_human_subjects must be an integer")
            elif nh < 0:
                _add_error(errors, "participants.num_human_subjects must be non-negative")

        # subject_ids
        if ids is None:
            _add_error(errors, "participants.subject_ids is missing")
        else:
            if not isinstance(ids, list):
                _add_error(errors, "participants.subject_ids must be a list")
            else:
                # check uniqueness
                if len(ids) != len(set(ids)):
                    _add_warning(warnings, "Duplicate entries found in participants.subject_ids")
                # check count consistency
                if isinstance(nh, int) and len(ids) != nh:
                    _add_error(errors, f"participants.num_human_subjects ({nh}) does not match length of subject_ids ({len(ids)})")

        # demographics mapping
        if demographics is None:
            _add_warning(warnings, "participants.demographics is missing")
        else:
            if not isinstance(demographics, dict):
                _add_error(errors, "participants.demographics must be a dictionary mapping subject_id -> demographics")
            else:
                # ensure each subject id has an entry
                if isinstance(ids, list):
                    for sid in ids:
                        if sid not in demographics:
                            _add_warning(warnings, f"Subject id '{sid}' missing in participants.demographics")
                # check fields for each demographic entry
                for sid, demo in demographics.items():
                    if not isinstance(demo, dict):
                        _add_error(errors, f"participants.demographics['{sid}'] must be an object/dict")
                    else:
                        # optional fields: age_group, gender, dominant_hand, experience_level
                        # flag if they are present but empty strings
                        for fld in ["age_group", "gender", "dominant_hand", "experience_level"]:
                            if fld in demo and isinstance(demo[fld], str) and demo[fld].strip() == "":
                                _add_warning(warnings, f"participants.demographics['{sid}'].{fld} is empty")

    # Validate configuration counts
    config_file = metadata.get("configuration_file", {})
    exec_policy = metadata.get("execution_policy", {})
    if isinstance(config_file, dict):
        cfg_num = config_file.get("num_configurations")
        if cfg_num is None:
            _add_error(errors, "configuration_file.num_configurations is missing")
        else:
            if not isinstance(cfg_num, int):
                _add_error(errors, "configuration_file.num_configurations must be an integer")
            elif cfg_num <= 0:
                _add_error(errors, "configuration_file.num_configurations must be positive")
    else:
        _add_error(errors, "configuration_file must be an object/dict")

    if isinstance(exec_policy, dict):
        exec_num = exec_policy.get("num_configurations")
        runs = exec_policy.get("runs_per_configuration")
        if exec_num is None:
            _add_error(errors, "execution_policy.num_configurations is missing")
        else:
            if not isinstance(exec_num, int):
                _add_error(errors, "execution_policy.num_configurations must be an integer")
            elif exec_num <= 0:
                _add_error(errors, "execution_policy.num_configurations must be positive")
        if isinstance(cfg_num, int) and isinstance(exec_num, int):
            if cfg_num != exec_num:
                _add_error(errors, f"configuration_file.num_configurations ({cfg_num}) != execution_policy.num_configurations ({exec_num})")
        if runs is None:
            _add_warning(warnings, "execution_policy.runs_per_configuration is missing")
        else:
            if not isinstance(runs, int) or runs <= 0:
                _add_error(errors, "execution_policy.runs_per_configuration must be a positive integer")
    else:
        _add_error(errors, "execution_policy must be an object/dict")

    # Validate environment.table_dimensions_mm
    env = metadata.get("environment", {})
    if not isinstance(env, dict):
        _add_error(errors, "environment must be an object/dict")
    else:
        td = env.get("table_dimensions_mm")
        if td is None:
            _add_warning(warnings, "environment.table_dimensions_mm is missing")
        else:
            if not isinstance(td, list):
                _add_error(errors, "environment.table_dimensions_mm must be a list of three numbers [length, width, height]")
            else:
                if len(td) != 3:
                    _add_error(errors, "environment.table_dimensions_mm must have exactly 3 elements")
                else:
                    # use numpy to check numeric and positive
                    try:
                        arr = np.array(td, dtype=float)
                        if np.any(arr <= 0):
                            _add_error(errors, "environment.table_dimensions_mm values must be positive numbers")
                    except Exception:
                        _add_error(errors, "environment.table_dimensions_mm must contain numeric values")

    # Validate annotation_protocol.video_fps
    ann = metadata.get("annotation_protocol", {})
    if isinstance(ann, dict):
        fps = ann.get("video_fps")
        if fps is None:
            _add_warning(warnings, "annotation_protocol.video_fps is missing")
        else:
            if not (isinstance(fps, int) and fps > 0):
                _add_error(errors, "annotation_protocol.video_fps must be a positive integer")
    else:
        _add_warning(warnings, "annotation_protocol missing or not an object")

    # Validate physical_assumptions.density_rice_g_per_ml
    phys = metadata.get("physical_assumptions", {})
    if isinstance(phys, dict):
        density = phys.get("density_rice_g_per_ml")
        if density is None:
            _add_warning(warnings, "physical_assumptions.density_rice_g_per_ml is missing")
        else:
            try:
                dval = float(density)
                if not (0.1 <= dval <= 2.0):
                    _add_warning(warnings, f"physical_assumptions.density_rice_g_per_ml ({dval}) is outside typical plausible range (0.1-2.0 g/ml)")
            except Exception:
                _add_error(errors, "physical_assumptions.density_rice_g_per_ml must be numeric")
    else:
        _add_warning(warnings, "physical_assumptions missing or not an object")

    # Validate hardware.sensors keys are booleans
    hw = metadata.get("hardware", {})
    if isinstance(hw, dict):
        sensors = hw.get("sensors")
        if sensors is None:
            _add_warning(warnings, "hardware.sensors is missing")
        else:
            if not isinstance(sensors, dict):
                _add_error(errors, "hardware.sensors must be an object/dict")
            else:
                for sname, sval in sensors.items():
                    if not isinstance(sval, bool):
                        _add_warning(warnings, f"hardware.sensors.{sname} expected boolean but got {type(sval).__name__}")

    # Validate camera_setup structure (basic)
    cam = env.get("camera_setup", {})
    if isinstance(cam, dict):
        # side_cameras should be list
        sc = cam.get("side_cameras")
        if sc is not None and not isinstance(sc, list):
            _add_warning(warnings, "environment.camera_setup.side_cameras should be a list")
        # overhead_camera should be dict or empty
        oc = cam.get("overhead_camera")
        if oc is not None and not isinstance(oc, dict):
            _add_warning(warnings, "environment.camera_setup.overhead_camera should be an object/dict")
    # Validate timestamps and strings that are likely required
    if isinstance(metadata.get("submission_timestamp"), str) and metadata.get("submission_timestamp").strip() == "":
        _add_warning(warnings, "submission_timestamp is empty")
    if isinstance(metadata.get("team"), str) and metadata.get("team").strip() == "":
        _add_warning(warnings, "team is empty")

    # Cross-check: video_recording_required vs annotation_protocol.video_annotation_used
    exec_video_required = exec_policy.get("video_recording_required") if isinstance(exec_policy, dict) else None
    ann_video_used = ann.get("video_annotation_used") if isinstance(ann, dict) else None
    if exec_video_required is True and ann_video_used is False:
        _add_warning(warnings, "execution_policy.video_recording_required is True but annotation_protocol.video_annotation_used is False")

    # Use pandas to create a small dataframe for subject demographics if available
    try:
        if isinstance(participants, dict) and isinstance(participants.get("demographics"), dict):
            demo = participants.get("demographics")
            # convert to DataFrame with one row per subject
            df = pd.DataFrame.from_dict(demo, orient='index')
            summary["demographics_table_shape"] = df.shape
            # flag if all demographic fields are empty for all subjects
            if df.applymap(lambda x: isinstance(x, str) and x.strip() == "").all().all():
                _add_warning(warnings, "All demographic fields are present but empty for all subjects")
    except Exception:
        _add_warning(warnings, "Failed to build demographics DataFrame for deeper checks")

    valid = len(errors) == 0
    return {
        "valid": valid,
        "errors": errors,
        "warnings": warnings,
        "summary": summary,
        "metadata": metadata
    }
 
 
# ============================================================================
# Evaluation Functions
# ============================================================================
def _validate_alignment_strategy(
    df_pred: pd.DataFrame, df_gts: pd.DataFrame, df_configs: pd.DataFrame
) -> str:
    """
    Decide alignment strategy:
      - "index": all three share identical index
      - "position": lengths equal but indices differ
      - raises ValueError if ambiguous
    """
    if df_pred.index.equals(df_gts.index) and df_pred.index.equals(df_configs.index):
        return "index"
    if len(df_pred) == len(df_gts) == len(df_configs):
        return "position"
    raise ValueError(
        "Cannot safely align df_pred, df_gts and df_configs: indices differ and lengths are not equal. "
        "Ensure they share the same index or have the same number of rows."
    )


def _select_subsets(
    df_pred: pd.DataFrame,
    df_gts: pd.DataFrame,
    df_configs: pd.DataFrame,
    col: str,
    val,
    strategy: str,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Return (pred_subset, gt_subset) for the given config column/value using the chosen strategy.
    - strategy == "index": use boolean mask on df_configs and select by index from df_pred/df_gts
    - strategy == "position": reset indices and select by position mask
    """
    if col not in df_configs.columns:
        # Column missing -> return empty subsets with same columns as originals
        return df_pred.iloc[0:0], df_gts.iloc[0:0]

    if strategy == "index":
        mask = df_configs[col].eq(val)
        idx = df_configs.index[mask]
        pred_subset = df_pred.loc[idx]
        gt_subset = df_gts.loc[idx]
        return pred_subset, gt_subset

    # position strategy
    cfg_vals = df_configs.reset_index(drop=True)[col]
    mask = cfg_vals.eq(val)
    pred_subset = df_pred.reset_index(drop=True).loc[mask]
    gt_subset = df_gts.reset_index(drop=True).loc[mask]
    return pred_subset, gt_subset


def run_grouped_evaluations(
    evaluator,
    df_pred: pd.DataFrame,
    df_gts: pd.DataFrame,
    df_configs: pd.DataFrame,
    target_location,
    results: Dict[str, Optional[float]],
    *,
    groups: Optional[List[Tuple[str, str, str]]] = None,
    empty_policy: str = "none",  # "none" -> None, "zero" -> 0.0
) -> pd.DataFrame:
    """
    Run evaluator for multiple groups, validate inputs, update results dict, and return a structured summary DataFrame.

    Args:
      evaluator: object with methods reset_all_scores(), run_benchmark_evaluation(pred, gt, target), get_benchmark_score()
      df_pred: predictions DataFrame
      df_gts: ground-truth DataFrame
      df_configs: configuration DataFrame (columns used for grouping: e.g., 'cup','fullness','grasp','location')
      target_location: passed to evaluator.run_benchmark_evaluation
      results: dict to be updated with descriptive keys for each group

    Returns:
      summary_df: DataFrame with columns:
        - group_type (e.g., 'cup', 'fullness', 'grasp', 'location')
        - group_value (e.g., 'white cup', 'empty', 'grasp1', 'left')
        - result_key (e.g., 'score_white_cup')
        - score (float or None)
        - score_pct (string like '95.00%' or empty string for None)
    """
    # Default declarative groups if not provided
    if groups is None:
        groups = [
            # cups
            ("cup", "white cup", "score_white_cup"),
            ("cup", "red cup", "score_red_cup"),
            ("cup", "beer cup", "score_beer_cup"),
            ("cup", "wine glass", "score_wine_glass"),
            # fullness
            ("fullness", "empty", "score_empty"),
            ("fullness", "filled", "score_filled"),
            # grasps
            ("grasp_type", "bottom", "score_grasp1"),
            ("grasp_type", "top", "score_grasp2"),
            ("grasp_type", "natural", "score_grasp3"),
            # locations
            ("handover_location", "left", "score_loc_left"),
            ("handover_location", "right", "score_loc_right"),
            ("handover_location", "center", "score_loc_centre"),
        ]

    # Decide alignment strategy
    strategy = _validate_alignment_strategy(df_pred, df_gts, df_configs)

    rows = []

    for col, val, key in groups:
        score_value: Optional[float] = None
        try:
            pred_subset, gt_subset = _select_subsets(df_pred, df_gts, df_configs, col, val, strategy)

            if pred_subset.empty or gt_subset.empty:
                # Apply empty policy
                if empty_policy == "zero":
                    score_value = 0.0
                else:
                    score_value = None
                results[key] = score_value
                logger.info("No rows for %s=%s; setting %s = %s", col, val, key, score_value)
            else:
                evaluator.reset_all_scores()
                evaluator.run_benchmark_evaluation(pred_subset, gt_subset, target_location)
                score_value = evaluator.get_benchmark_score()
                results[key] = score_value

        except Exception as exc:
            logger.exception("Evaluation failed for %s=%s (key=%s): %s", col, val, key, exc)
            results[key] = None
            score_value = None

        # Format percentage string (two decimals) or empty string for None
        if score_value is None or (isinstance(score_value, float) and pd.isna(score_value)):
            score_pct = ""
        else:
            try:
                score_pct = f"{float(score_value) * 100:.2f}%"
            except Exception:
                score_pct = ""

        rows.append(
            {
                "group_type": col,
                "group_value": val,
                "result_key": key,
                "score": score_value,
                "score_pct": score_pct,
            }
        )

    summary_df = pd.DataFrame(rows)

    # Return a structured summary (one row per group)
    return summary_df
 
def run_benchmark_evaluation(args) -> dict:
    """
    Execute the benchmark evaluation pipeline.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        dict: Evaluation results containing all scores
        
    Raises:
        RuntimeError: If evaluation fails
    """
    # Import here to avoid dependency if not using benchmark mode
    try:
        from benchmark_evaluator import CorsmalEvaluationToolkit
    except ImportError:
        raise RuntimeError(
            "benchmark_evaluator module not found. "
            "Ensure benchmark_evaluator.py is in the Python path."
        )
    
    logger.info("=" * 70)
    logger.info("Starting CORSMAL Benchmark Evaluation")
    logger.info("=" * 70)
    
    try:
        # Step 1: Load and validate CSVs
        logger.info("Step 1: Loading and validating input files...")

        try:
            from benchmark.submission_validator import SubmissionValidator
        except ImportError:
            raise RuntimeError(
                "submission_validator module not found. "
                "Ensure submission_validator.py is in the Python path."
            )

        validator = SubmissionValidator()
        is_valid = validator.validate_file(args.submission_csv)
        validator.print_report()
    
        summary = validator.get_summary()
        print(f"\nSummary: {summary['total_rows']} rows, {summary['errors']} errors, {summary['warnings']} warnings")

        df_pred = validator.get_dataframe()
        
        df_gts = validate_ground_truth_csv(args.ground_truth_csv)

        report = validate_metadata_json(args.metadata)
        print("Valid:", report["valid"])
        if report["errors"]:
            print("Errors:")
            for e in report["errors"]:
                print(" -", e)
        if report["warnings"]:
            print("Warnings:")
            for w in report["warnings"]:
                print(" -", w)
        print("Summary:", report["summary"])

        target_location = np.asarray(report["metadata"]["execution_policy"]["target_delivery_location"])

        configs_fn = os.path.join("resources", "benchmark", "benchmark_configs.csv")
        df_configs = load_configs(configs_fn)
        
        
        # Step 2: Initialize evaluator
        logger.info("Step 2: Initializing CORSMAL Evaluation Toolkit...")
        evaluator = CorsmalEvaluationToolkit(
            n_config_cup=args.n_config_cup,
            n_subjects=args.n_subjects,
            n_cups=args.n_cups
        )
        logger.debug(f"Evaluator initialized with {evaluator.n_configs} total configurations")
        
        # Step 3: Run benchmark evaluation
        logger.info("Step 3: Running benchmark evaluation...")
        evaluator.run_benchmark_evaluation(df_pred, df_gts, target_location)
        
        # Step 4: Extract results
        logger.info("Step 4: Extract results...")
        results = evaluator.get_all_scores()
        results["team"] = report["metadata"]["team"]
        groups_res = run_grouped_evaluations(evaluator, df_pred, df_gts, df_configs, target_location, results)

        logger.info("✓ Benchmark evaluation completed successfully")
        return results
        
    except Exception as e:
        logger.error(f"Benchmark evaluation failed: {e}")
        raise RuntimeError(f"Evaluation failed: {e}")
 
 
def run_challenge_evaluation(args) -> dict:
    """
    Execute challenge mode evaluation (prediction format validation only).
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        dict: Validation results
    """
    logger.info("=" * 70)
    logger.info("Running Challenge Mode Evaluation")
    logger.info("=" * 70)
    
    try:
        logger.info("Validating submission format...")
        df_pred = validate_prediction_csv(args.submission_csv)
        
        results = {
            "status": "valid",
            "message": "Submission format is valid",
            "shape": df_pred.shape,
            "columns": list(df_pred.columns),
            "rows_count": len(df_pred)
        }
        
        logger.info("✓ Challenge validation passed")
        return results
        
    except Exception as e:
        logger.error(f"Challenge validation failed: {e}")
        raise RuntimeError(f"Validation failed: {e}")
    
# ============================================================================
# Results Export & Reporting Functions
# ============================================================================
 
def ensure_output_directory(output_dir: str) -> str:
    """
    Ensure output directory exists; create if necessary.
    
    Args:
        output_dir: Path to output directory
        
    Returns:
        str: Absolute path to output directory
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    logger.info(f"Output directory ready: {output_dir}")
    return output_dir
 

from datetime import datetime
def save_results(results: dict, output_dir: str) -> None:
    """
    Save evaluation results to CSV file.

    Args:
        results: Dictionary of results from evaluation
        output_dir: Directory to save results
    """
    ensure_output_directory(output_dir)

    # Stable schemas
    VISION_SCHEMA = ["width_top", "width_bottom", "height", "mass", "fullness"]
    ROBOT_SCHEMA = ["mass_robot", "hand_pose", "end_effector"]
    TASK_SCHEMA = [
        "delivery_location",
        "delivery_mass_filling",
        "time_human_maneuvering",
        "time_handover",
        "time_robot_maneuvering"
    ]

    GROUP_SCHEMA = [
        "benchmark_score",
        "score_white_cup", "score_red_cup", "score_beer_cup", "score_wine_glass", 
        "score_empty", "score_filled", "score_grasp1", "score_grasp2", "score_grasp3", 
        "score_loc_left", "score_loc_right", "score_loc_centre"
    ]

    try:
        # --- Vision ---
        if "vision" in results:
            vision_df = pd.DataFrame([results["vision"]], index=["scores"])
        else:
            vision_df = pd.DataFrame(
                {k: 0.0 for k in VISION_SCHEMA},
                index=["scores"]
            )

        # --- Robot ---
        if "robot" in results:
            robot_df = pd.DataFrame([results["robot"]], index=["scores"])
        else:
            robot_df = pd.DataFrame(
                {k: 0.0 for k in ROBOT_SCHEMA},
                index=["scores"]
            )

        # --- Task ---
        if "task" in results:
            task_df = pd.DataFrame([results["task"]], index=["scores"])
        else:
            task_df = pd.DataFrame(
                {k: 0.0 for k in TASK_SCHEMA},
                index=["scores"]
            )

        # --- Group scores ---
        group_scores = results.get("group_scores", {})
        groups_df = pd.DataFrame(
            {
                "vision_score": group_scores.get("vision_score"),
                "robot_score": group_scores.get("robot_score"),
                "task_score": group_scores.get("task_score"),
            } | {k: results.get(k) for k in GROUP_SCHEMA},
            index=["scores"]
        )

        # --- Metadata ---
        info_res = pd.DataFrame(
            {
                "Timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                "team": [results.get("team", "unknown")]
            },
            index=["scores"]
        )

        # --- Final concatenation ---
        summary_df = pd.concat(
            [info_res, vision_df, robot_df, task_df, groups_df],
            axis=1
        )

        # --- Convert numeric columns (except Timestamp and team) to percentage strings ---
        exclude_cols = {"Timestamp", "team"}
        for col in summary_df.columns:
            if col in exclude_cols:
                continue

            def _to_percent_str(val):
                if pd.isna(val):
                    return ""
                try:
                    num = float(val)
                except Exception:
                    return str(val)
                # Multiply by 100 and format with two decimals
                return f"{num * 100:.2f}%"

            summary_df[col] = summary_df[col].apply(_to_percent_str)

        # --- Append to CSV if exists, otherwise create with header ---
        out_path = os.path.join(output_dir, "scores_res.csv")
        file_exists = os.path.exists(out_path)

        # Use mode 'a' to append; write header only if file does not exist
        summary_df.to_csv(out_path, mode="a", header=not file_exists, index=False)


        logger.info("✓ Results saved to CSV format")

    except Exception as e:
        logger.error(f"Failed to save results: {e}")
        raise
 
 
def print_results_summary(results: dict) -> None:
    """
    Print a formatted summary of evaluation results to console.
    
    Args:
        results: Dictionary of results from evaluation
    """
    logger.info("=" * 70)
    logger.info("EVALUATION RESULTS SUMMARY")
    logger.info("=" * 70)
    
    # Print main scores
    logger.info(f"Benchmark Score:  {results.get('benchmark_score', 0.0)*100:.2f}")

    group_scores = results.get("group_scores", {})
    if group_scores:
        logger.info(f"Vision Score:     {group_scores.get('vision_score', 0.0)*100:.2f}")
        logger.info(f"Robot Score:      {group_scores.get('robot_score', 0.0)*100:.2f}")
        logger.info(f"Task Score:       {group_scores.get('task_score', 0.0)*100:.2f}")
    
    # Print detailed scores if available
    if results.get("vision"):
        logger.info("-" * 70)
        logger.info("Detailed Vision Scores:")
        for key, val in results["vision"].items():
            logger.info(f"  {key:20s}: {val*100:.2f}")
    
    if results.get("robot"):
        logger.info("Detailed Robot Scores:")
        for key, val in results["robot"].items():
            logger.info(f"  {key:20s}: {val*100:.2f}")
    
    if results.get("task"):
        logger.info("Detailed Task Scores:")
        for key, val in results["task"].items():
            logger.info(f"  {key:20s}: {val*100:.2f}")
    
    logger.info("=" * 70)

# ============================================================================
# Argument Parser
# ============================================================================

from argparse import ArgumentParser
def get_parser() -> ArgumentParser:
    """
    Create and configure the argument parser for the CORSMAL Evaluation Toolkit.
 
    Returns:
        argparse.ArgumentParser: Configured parser with CLI arguments.
    """
    parser = argparse.ArgumentParser(
        description="CORSMAL Evaluation Toolkit - Benchmark Human-to-Robot Handover Performance",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "--mode",
        choices=["challenge", "benchmark", "competition"],
        required=True,
        help="Run in specified mode."
    )
 
    # Mode Selection (mutually exclusive)
    # mode_group = parser.add_mutually_exclusive_group(required=True)
    # mode_group.add_argument(
    #     "--challenge",
    #     action="store_true",
    #     help="Run in challenge mode (predictions only, no ground truth)."
    # )
    # mode_group.add_argument(
    #     "--benchmark",
    #     action="store_true",
    #     help="Run in benchmark mode (requires ground truth for evaluation)."
    # )
 
    # Input Files
    parser.add_argument(
        "--submission_csv",
        required=True,
        type=existing_file,
        help="Path to the submission CSV file with predictions."
    )

    parser.add_argument(
        "--metadata",
        type=existing_file,
        default=None,
        help="Path to the ground truth CSV file (required for --benchmark mode)."
    )
 
    parser.add_argument(
        "--ground_truth_csv",
        type=existing_file,
        default=None,
        help="Path to the ground truth CSV file (required for --benchmark mode)."
    )
 
    # Benchmark Configuration
    parser.add_argument(
        "--n_config_cup",
        type=int,
        default=18,
        help="Number of configurations per cup type."
    )
    parser.add_argument(
        "--n_subjects",
        type=int,
        default=4,
        help="Number of human subjects in the benchmark."
    )
    parser.add_argument(
        "--n_cups",
        type=int,
        default=4,
        help="Number of cup types in the benchmark."
    )
 
    # Output Options
    parser.add_argument(
        "--output_dir",
        type=str,
        default="./evaluation_results",
        help="Directory to save evaluation results and reports."
    )
    parser.add_argument(
        "--save_detailed",
        action="store_true",
        help="Save detailed per-trial results and aggregated statistics."
    )
 
    # Advanced Options
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging output."
    )
    parser.add_argument(
        "--validate_only",
        action="store_true",
        help="Validate input CSV format without running evaluation."
    )

    return parser

# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    logger.info("Initialising CORSMAL Evaluation Toolkit...")
    logger.info(f"Python {sys.version_info.major}.{sys.version_info.minor}")
 
    # Optional: Show OpenCV version if installed
    try:
        import cv2
        logger.info(f"OpenCV {cv2.__version__}")
    except ImportError:
        logger.debug("OpenCV not installed")
 
    try:
        # Parse CLI arguments
        parser = get_parser()
        args = parser.parse_args()
        
        # Set logging level based on verbose flag
        if args.verbose:
            logger.enable("__main__")
        
        logger.debug(f"Arguments: {args}")

        # Validate benchmark mode requirements
        if args.mode == "benchmark" and not args.ground_truth_csv:
            parser.error("--ground_truth_csv is required when using benchmark mode")
 
        # Validate-only mode
        if args.validate_only:
            logger.info("Running in validation-only mode...")
            df_pred = validate_prediction_csv(args.submission_csv)
            logger.info("✓ Validation successful - CSV format is correct")
            sys.exit(0)
 
        # Run selected mode
        results = None

        # Example: Mode selection
        if args.mode == "challenge":
            logger.info("Running in challenge mode...")
            # results = run_challenge_evaluation(args)

        elif args.mode == "benchmark":
            logger.info("Running in benchmark mode...")
            results = run_benchmark_evaluation(args)

        elif args.mode == "competition":
            logger.info("Running in competition mode...")
        else:
            logger.warning("No mode selected. Choose between challenge, benchmark, competition.")
        
        # Print results
        if results:
            print_results_summary(results)
            
            # Save results if output directory specified
            if args.output_dir:
                save_results(results, args.output_dir)
                logger.info(f"Results saved to: {args.output_dir}")
 
        logger.info("Evaluation completed successfully")
        sys.exit(0)

    except argparse.ArgumentError as e:
        logger.error(f"Argument parsing failed: {e}")
        sys.exit(1)
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        sys.exit(1)
    except RuntimeError as e:
        logger.error(f"Runtime error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        sys.exit(1)
