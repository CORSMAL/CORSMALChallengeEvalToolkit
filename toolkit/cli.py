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
 
import pandas as pd
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
        required_columns = [
            "w^i (mm)", "w^i_b (mm)", "h^i (mm)",
            "m^i_v (grams)", "f^i (%)"
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
            "width_at_the_top", "width_at_the_bottom", "height", "volume"
        ]
        validate_csv_columns(df, required_columns, "ground truth")
        return df
        
    except pd.errors.ParserError as e:
        raise ValueError(f"Failed to parse ground truth CSV: {e}")
    except Exception as e:
        raise ValueError(f"Error loading ground truth CSV: {e}")
 
 
# ============================================================================
# Evaluation Functions
# ============================================================================
 
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
        df_pred = validate_prediction_csv(args.submission_csv)
        df_gts = validate_ground_truth_csv(args.ground_truth_csv)
        
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
        evaluator.run_benchmark_evaluation(df_pred, df_gts)
        
        # Step 4: Compute group scores
        logger.info("Step 4: Computing aggregated scores...")
        evaluator.compute_vision_score()
        evaluator.compute_robot_score()
        evaluator.compute_task_score()
        evaluator.compute_benchmark_score()
        
        # Step 5: Extract results
        results = {
            "individual_scores": evaluator.get_all_scores(),
            "benchmark_score": evaluator.get_benchmark_score(),
            "vision_score": evaluator.get_vision_score(),
            "robot_score": evaluator.get_robot_score(),
            "task_score": evaluator.get_task_score(),
        }
        
        # Optionally compute detailed aggregations
        if args.save_detailed:
            logger.info("Computing aggregated statistics...")
            results["aggregated_stats"] = evaluator.compute_aggregated_scores()
        
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
 
 
def save_results(results: dict, output_dir: str, output_format: str = "csv") -> None:
    """
    Save evaluation results to file(s).
    
    Args:
        results: Dictionary of results from evaluation
        output_dir: Directory to save results
        output_format: Format to save in ("json", "csv", or "both")
    """
    ensure_output_directory(output_dir)
    
    scores = results.get("individual_scores", {})
    
    try:
        if output_format in ["csv", "both"]:
            # Save vision scores
            if "vision" in scores:
                vision_df = pd.DataFrame([scores["vision"]], index=["scores"])
                vision_df.to_csv(os.path.join(output_dir, "vision_scores.csv"))
            
            # Save robot scores
            if "robot" in scores:
                robot_df = pd.DataFrame([scores["robot"]], index=["scores"])
                robot_df.to_csv(os.path.join(output_dir, "robot_scores.csv"))
            
            # Save task scores
            if "task" in scores:
                task_df = pd.DataFrame([scores["task"]], index=["scores"])
                task_df.to_csv(os.path.join(output_dir, "task_scores.csv"))
            
            # Save summary
            summary_df = pd.DataFrame({
                "Score Type": ["Vision", "Robot", "Task", "Benchmark"],
                "Score": [
                    results.get("vision_score", 0.0),
                    results.get("robot_score", 0.0),
                    results.get("task_score", 0.0),
                    results.get("benchmark_score", 0.0)
                ]
            })
            summary_df.to_csv(os.path.join(output_dir, "summary_scores.csv"), index=False)
            logger.info("✓ Results saved to CSV format")
        
        if output_format in ["json", "both"]:
            # Convert numpy types to native Python types for JSON serialization
            results_json = json.loads(json.dumps(results, default=str))
            with open(os.path.join(output_dir, "evaluation_results.json"), "w") as f:
                json.dump(results_json, f, indent=2)
            logger.info("✓ Results saved to JSON format")
            
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
    logger.info(f"Benchmark Score:  {results.get('benchmark_score', 0.0):.4f}")
    logger.info(f"Vision Score:     {results.get('vision_score', 0.0):.4f}")
    logger.info(f"Robot Score:      {results.get('robot_score', 0.0):.4f}")
    logger.info(f"Task Score:       {results.get('task_score', 0.0):.4f}")
    
    # Print detailed scores if available
    individual_scores = results.get("individual_scores", {})
    
    if individual_scores.get("vision"):
        logger.info("-" * 70)
        logger.info("Detailed Vision Scores:")
        for key, val in individual_scores["vision"].items():
            logger.info(f"  {key:20s}: {val:.4f}")
    
    if individual_scores.get("robot"):
        logger.info("Detailed Robot Scores:")
        for key, val in individual_scores["robot"].items():
            logger.info(f"  {key:20s}: {val:.4f}")
    
    if individual_scores.get("task"):
        logger.info("Detailed Task Scores:")
        for key, val in individual_scores["task"].items():
            logger.info(f"  {key:20s}: {val:.4f}")
    
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
    parser.add_argument(
        "--output_format",
        choices=["json", "csv", "both"],
        default="csv",
        help="Output format for results."
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
                save_results(results, args.output_dir, args.output_format)
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
