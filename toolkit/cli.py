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
# Modified Date: 2026/03/20
################################################################################## 

import os
import sys
import argparse

from loguru import logger

# Configure logger
logger.remove()  # Remove default handler
logger.add(sys.stderr, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                              "<level>{level: <8}</level> | "
                              "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                              "<level>{message}</level>",
           level="DEBUG")

def ensure_csv_exists(path: str) -> str:
    """
    Ensure the CSV file exists. If not, create a template file.
    """
    if not os.path.isfile(path):
        logger.info(f"CSV file not found: {path}. Creating a template...")
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("id,value\n")  # Example header
            logger.info(f"Template CSV created at: {path}")
        except OSError as e:
            raise argparse.ArgumentTypeError(f"Cannot create file {path}: {e}")
    return path

def existing_file(path: str) -> str:
    """
    Validate that the given path points to an existing file.
    Raises argparse.ArgumentTypeError if not found.
    """
    if not os.path.isfile(path):
        raise argparse.ArgumentTypeError(f"File not found: {path}")
    return path

from argparse import ArgumentParser
def get_parser() -> ArgumentParser:
    """
    Create and configure the argument parser for the CORSMAL Evaluation Toolkit.

    Returns:
        argparse.ArgumentParser: Configured parser with CLI arguments.
    """
    parser = argparse.ArgumentParser(
        description="CORSMAL Evaluation Toolkit",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "--challenge",
        action="store_true",
        help="Run in challenge mode."
    )
    parser.add_argument(
        "--benchmark",
        action="store_true",
        help="Run in benchmark mode."
    )
    parser.add_argument(
        "--submission_csv",
        default="random.csv",
        type=existing_file,  # Validation here
        help="Path to the submission CSV file."
    )

    return parser


if __name__ == "__main__":
    logger.info("Initialising...")
    logger.info(f"Python {sys.version_info.major}.{sys.version_info.minor}")

    # Optional: Show OpenCV version if installed
    try:
        import cv2
        logger.info(f"OpenCV {cv2.__version__}")
    except ImportError:
        logger.warning("OpenCV not installed.")

    try:
        # Parse CLI arguments
        parser = get_parser()
        args = parser.parse_args()

        # Debug: Show parsed arguments
        logger.debug(f"Arguments received: {args}")

        # Example: Mode selection
        if args.challenge:
            logger.info("Running in challenge mode...")
        elif args.benchmark:
            logger.info("Running in benchmark mode...")
        else:
            logger.warning("No mode selected. Use --challenge or --benchmark.")

    except argparse.ArgumentError as e:
        logger.error(f"Argument parsing failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        sys.exit(1)