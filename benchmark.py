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
#  Created Date: 2023/01/11
# Modified Date: 2026/03/20
#
# MIT License

# Copyright (c) 2023-2026 CORSMAL

# Permission is hereby granted, free of charge, to any person obtaining a 
# copy of this software and associated documentation files (the "Software"), 
# to deal in the Software without restriction, including without limitation 
# the rights to use, copy, modify, merge, publish, distribute, sublicense, 
# and/or sell copies of the Software, and to permit persons to whom the 
# Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in 
# all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
# FROM, # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
# DEALINGS IN THE SOFTWARE.
#----------------------------------------------------------------------------
"""
TODO:
 - [ ] implement sigma_3()
 - [ ] implement s7_s8()
 - [ ] add functions from the 'challenge' script
 - [ ] read .xlsx file and compute the scores

NOTE
I don't know how to compute the mass of the filling. We only have the filling amount in millilitre, but to compute mass,
you need to convert it to grams. So you need to know how much the filling per ml weighs in grams. 
The ground-truths were done in white rice,
which is about 0.81g per 1ml. But the predictions could have used different rice, which could have a different weighing factor.
"""

import os
import sys
import argparse
import pandas as pd
import json
import numpy as np

from loguru import logger

# Configure logger
logger.remove()  # Remove default handler
logger.add(sys.stderr, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                              "<level>{level: <8}</level> | "
                              "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                              "<level>{message}</level>",
           level="DEBUG")



def get_measure_annotations(df_annotations, measure, n_config_cup, n_subjects):
    ''' 
    Return all the annotations for a given measure as a numpy array from an input pandas dataframe. 

    Arguments:
        - df_annotations: pandas datframe with all the annotations
        - measure: width_at_the_top, width_at_the_bottom, height
        - n_config_cup: number of configuration for each cup. Default: 18
        - n_subjects: number of subjects. Default: 4
    '''

    assert(measure in ['width_at_the_top','width_at_the_bottom', 'height', 
        'volume'])

    measure_annotations = []

    if measure == 'volume':
        cups = df_annotations.loc[:, "cup"]
        fillings = df_annotations.loc[:, "filling (ml)"]

        for j in range(0, n_configs):
            current_filling = fillings[j]
            current_cup_str = "cup{}".format(cups[j])
            
            current_volume = df_annotations[measure][current_cup_str]
            gt_fullness = current_filling / current_volume * 100
            
            measure_annotations.append(gt_fullness)
    else:
        cup1_18 = np.repeat(df_annotations[measure]["cup1"], n_config_cup)
        cup2_18 = np.repeat(df_annotations[measure]["cup2"], n_config_cup)
        cup3_18 = np.repeat(df_annotations[measure]["cup3"], n_config_cup)
        cup4_18 = np.repeat(df_annotations[measure]["cup4"], n_config_cup)
        
        cups_all = np.concatenate([cup1_18, cup2_18, cup3_18, cup4_18])
        
        measure_annotations = np.tile(cups_all, n_subjects)

    return measure_annotations


def check_length_arrays(array1, array2):
    if len(array1) != len(array2):
        raise Exception(
                "Number of predictions != number of annotations!")

###############################################################################
class CorsmalEvaluationToolkit():
    def __init__(self):
        self.n_config_cup = 18
        self.n_subjects = 4
        self.n_cups = 4

        self.n_configs = self.n_config_cup * self.n_subjects * self.n_cups

        reset_all_scores()


    def reset_all_scores(self):
        # Vision scores
        self.width_top = 0               # in mm
        self.width_bottom = 0            # in mm
        self.height = 0                  # in mm  
        self.mass = 0                    # in g (cup + filling)
        self.fullness = 0                # in %

        # Robot scores
        self.mass_robot = 0              # in mm
        self.hand_pose = 0               # in mm, degrees
        self.end_effector = 0            # in mm, degrees

        # Task scores
        self.delivery_location = 0       # in mm
        self.delivery_mass_filling = 0   # in grams
        self.time_human_maneuvering = 0  # in mm
        self.time_handover = 0           # in mm
        self.time_robot_maneuvering = 0  # in mm

        # Group scores
        self.vision_score = 0
        self.robot_score = 0
        self.task_score = 0
        
        self.benchmark_score = 0


    # Sigma functions
    def compute_score_type_1(self, a, b):
        if a == 0 and b == 0:
            return 1
        
        diff_a_b = np.abs(a-b)
        if diff_a_b >= b:
            return 0
        
        return 1 - ( diff_a_b / b)    

    def compute_score_type_2(self, a, eta):
        if a < eta:
            return 1 - (a/eta)
        else:
            return 0

    def compute_score_type_3(self, P, P_hat, epsilon):
        # NOTE: I do not know the exact dimensions of P - therefore I left it 
        # as a TODO for the moment
        return 0


    def compute_width_top(self, preds, gts):
        check_length_preds_gts(preds, gts)
        
        width_top = 0
        for pred, gt in zip(preds, gts):
            width_top += sigma_1(pred, gt)
        
        self.width_top = width_top / len(preds)


    def compute_width_bottom(self, preds, gts):
        check_length_preds_gts(preds, gts)
        
        width_bottom = 0
        for pred, gt in zip(preds, gts):
            width_bottom += sigma_1(pred, gt)
        
        self.width_bottom = width_bottom / len(preds)


    def compute_height(self, pred, gts):
        check_length_preds_gts(preds, gts)
        
        height = 0
        for pred, gt in zip(preds, gts):
            height += sigma_1(pred, gt)
        
        self.height = height / len(preds)


    def compute_mass_vision(self, preds, gts):
        check_length_preds_gts(preds, gts)
        
        mass = 0
        for pred, gt in zip(preds, gts):
            mass += sigma_1(pred, gt)
        
        self.mass = mass / len(preds)


    def compute_fullness(self, preds, gts):
        check_length_preds_gts(preds, gts)
        
        fullness = 0
        for pred, gt in zip(preds, gts):
            fullness += (1 - (np.abs(pred - gt) / 100))
        
        self.fullness = fullness / len(preds)


    def compute_vision_score(self):
        vision_score =  self.width_top / 9
                        + self.width_bottom / 9
                        + self.height / 9
                        + self.mass / 3
                        + self.fullness /3

        self.vision_score = vision_score


    def compute_mass_robot(self, preds, gts):
        check_length_preds_gts(preds, gts)
        
        mass = 0
        for pred, gt in zip(preds, gts):
            mass += sigma_1(pred, gt)
        
        self.mass_robot = mass / len(preds)

    def compute_human_hand_pose_prediction(self, preds, gts, epsilon):
        hand_pose = compute_score_type_3(preds, gts. epsilon)
        self.hand_pose = hand_pose

    def compute_end_effector(self, preds, gts, epsilon):
        end_effector = compute_score_type_3(preds, gts. epsilon)
        self.end_effector = end_effector


     def compute_robot_score(self):
        robot_score =  self.mass_robot + self.hand_pose + self.end_effector
        self.robot_score = robot_score / 3

    
    def compute_benchmark_score(self):
        benchmark_score = self.vision_score 
                        + self.robot_score 
                        + self.task_score
        
        benchmark_score /= 3
        self.benchmark_score = benchmark_score
    

    def get_vision_score(self):
        return self.vision_score

    def get_robot_score(self):
        return self.robot_score

    def get_task_score(self):
        return self.task_score

    def get_benchmark_score(self):
        return self.benchmark_score


    def run_benchmark_evaluation(self, df_pred, df_gts):
        
        # Width at the top
        width_top_pr = df_pred.loc[:, "w^i (mm)"]        
        width_top_gt = get_measure_annotations(df_gts, 'width_at_the_top', 
                self.n_config_cup, self.n_subjects)
        
        self.compute_width_top(width_top_pr, width_top_gt)

        # Width at the bottom
        width_bottom_pr = df_pred.loc[:, "w^i_b (mm)"]        
        width_bottom_gt = get_measure_annotations(df_gts, 
            'width_at_the_bottom', self.n_config_cup, self.n_subjects)
        
        self.compute_width_bottom(width_bottom_pr, width_bottom_gt)

        # Height
        height_pr = df_pred.loc[:, "h^i (mm)"]        
        height_gt = get_measure_annotations(df_gts, 'height', 
                self.n_config_cup, self.n_subjects)
        
        self.compute_height(height_pr, height_gt)

        # Mass (vision)
        mass_v_pr = df_pred.loc[:, "m^i_v (grams)"]
        mass_v_gt = None

        self.compute_mass_vision(mass_v_pr, mass_v_gt)

        # Fullness
        fullnesses_pr = df_pred.loc[:, "f^i (%)"] 
        fullnesses_gt = get_measure_annotations(df_gts, 'volume', 
                self.n_config_cup, self.n_subjects)
        
        self.compute_fullness(fullnesses_pr, fullnesses_gt)

##################################################################################
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


# Group: Task
def s9_s11_s12_s13(preds, thr):
    running_scores = 0
    for pred in preds:
        running_scores += sigma_2(pred, thr)
    return running_scores / len(preds)

def Sg(lambdas, s9, s11, s12, s13):
    return lambdas[8] * s9 + lambdas[10] * s11 + lambdas[11] * s12 + lambdas[12] * s13


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

    #create_new_pandaframe_submission_form()
    

def run_benchmark(args):        
        # Read .json dictionary containing the ground-truths
        f = open('benchmark_groundtruths.json')
        GTs = json.load(f)

        # Read .xlsx file containing the predictions
        #PREDs_df = pd.read_excel(args.submission_xlsx, 'Measures')
        df = pd.read_csv(args.submission_csv)
        print(df)

        # Get the configuration data from the dataframe
        configurations = df.loc[:, "configuration"]
        cups = df.loc[:, "cup"]
        fillings = df.loc[:, "filling (ml)"]
        grasp_types = df.loc[:, "grasp type"]
        handover_locations = df.loc[:, "handover location"]
        subjects = df.loc[:, "subject"]
        
        # Get the predictions from the column from the dataframe    
        predicted_mirs = df.loc[:, "m^i_r (grams)"]     # mass - robot
        predicted_dis = df.loc[:, "d^i (mm)"]           # delivery location
        predicted_wis_g = df.loc[:, "w^i (grams)"]      # mass of delivered filling
        predicted_tihms1 = df.loc[:, "t^i_{hm} (ms)"]   # human maneuvering time
        predicted_tihms2 = df.loc[:, "t^i_{ho} (ms)"]   # handover time
        predicted_tirms = df.loc[:, "t^i_{rm} (ms)"]    # robot maneuvering time

        #print("Predicted WIS:\n", predicted_wis_mm.to_numpy())

        print("\nComputed scores")
        print("s1 :", s1)
        
        # s4 - NOTE: I'm not sure how to compute the mass of the filling
        print("s4 : not implemented yet.")
        
        # s6 - NOTE: same as note for s4: I don't know how to compute the mass of the filling
        print("s6 : not implemented yet.")
        
        # s7
        print("s7 : not implemented yet.")

        # s8
        print("s8 : not implemented yet.")

        # s9
        thr = 50
        s9 = s9_s11_s12_s13(predicted_dis, thr)
        print("s9 :", s9, "| Note: this was with a threshold of {}".format(thr))

        # s10
        s10 = s1_s2_s3_s4_s6_s10(predicted_wis_g, fillings)
        print("s10:", s10)
        
        # s11
        s11 = s9_s11_s12_s13(predicted_tihms1, thr)
        print("s11:", s11, "| Note: this was with a threshold of {}".format(thr))
        
        # s12
        s12 = s9_s11_s12_s13(predicted_tihms2, thr)
        print("s12:", s12, "| Note: this was with a threshold of {}".format(thr))

        # s13
        s13 = s9_s11_s12_s13(predicted_tirms, thr)
        print("s13:", s13, "| Note: this was with a threshold of {}".format(thr))

        # TODO: save the scores
        

    print("\nRan succesfully!\n")


# predicted_wibs = PREDs_df.iloc[3:, 7]     # s2  : width at bottom
# predicted_his = PREDs_df.iloc[3:, 8]      # s3  : height
# predicted_mivs = PREDs_df.iloc[3:, 9]     # s4  : mass (cup+filling) - vision
# predicted_fis = PREDs_df.iloc[3:, 10]     # s5  : fullness
# predicted_mirs = PREDs_df.iloc[3:, 11     # s6  : mass (cup+filling) - robot
# predicted_dis = PREDs_df.iloc[3:, 12]     # s9  : delivery location
# predicted_wis = PREDs_df.iloc[3:, 13]     # s10 : mass of the delivered filling
# predicted_tihms1 = PREDs_df.iloc[3:, 14]  # s11 : human maneuvering time
# predicted_tihms2 = PREDs_df.iloc[3:, 15]  # s12 : handover
# predicted_tirms = PREDs_df.iloc[3:, 16]   # s13 : robot maneuvering