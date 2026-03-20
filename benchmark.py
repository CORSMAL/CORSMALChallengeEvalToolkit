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
import pandas as pd
import json

from loguru import logger

# Configure logger
logger.remove()  # Remove default handler


#create_new_pandaframe_submission_form()
    
from corsmal_toolkit.benchmark_evaluator import CorsmalEvaluationToolkit as BenchmarkEvaluator

def run_benchmark(args):
    """
    Run the full RA-L 2020 benchmark evaluation.
    Produces overall and per-category aggregated scores.
    """
    # -------------------------
    # Load ground truths
    # -------------------------
    with open(args.groundtruth_json, 'r') as f:
        GTs = json.load(f)

    # -------------------------
    # Load predictions
    # -------------------------
    df = pd.read_csv(args.submission_csv)

    evaluator = BenchmarkEvaluator()

    # -------------------------
    # Loop over each trial
    # -------------------------
    for idx, row in df.iterrows():
        # ---- Vision metrics (s1–s5) ----
        evaluator.compute_width_top([row["width_top_pred_mm"]], [GTs["width_top_mm"][idx]])
        evaluator.compute_width_bottom([row["width_bottom_pred_mm"]], [GTs["width_bottom_mm"][idx]])
        evaluator.compute_height([row["height_pred_mm"]], [GTs["height_mm"][idx]])
        evaluator.compute_mass_vision([row["mass_vision_pred_g"]], [GTs["mass_g"][idx]])
        evaluator.compute_fullness([row["fullness_pred_pct"]], [GTs["fullness_pct"][idx]])
        S_vision = evaluator.compute_vision_score()

        # ---- Robot metrics (s6–s8) ----
        evaluator.compute_mass_robot([row["m^i_r (grams)"]], [GTs["mass_g"][idx]])
        evaluator.compute_human_hand_pose_prediction(
            [row["human_hand_pose_pred"]], [GTs["human_hand_pose_gt"][idx]]
        )
        evaluator.compute_end_effector(
            [row["end_effector_pose_pred"]], [GTs["end_effector_pose_gt"][idx]]
        )
        S_robot = evaluator.compute_robot_score()

        # ---- Task metrics (s9, s11–s14) ----
        evaluator.compute_delivery_location([row["d^i (mm)"]], thr_mm=50.0)
        evaluator.compute_delivery_mass_filling([row["w^i (grams)"]], thr_g=50.0)
        evaluator.compute_time_human_maneuvering([row["t^i_{hm} (ms)"] / 1000.0], thr_s=10.0)
        evaluator.compute_time_handover([row["t^i_{ho} (ms)"] / 1000.0], thr_s=5.0)
        evaluator.compute_time_robot_maneuvering([row["t^i_{rm} (ms)"] / 1000.0], thr_s=15.0)
        S_task = evaluator.compute_task_score()

        # ---- Benchmark score ----
        S_benchmark = evaluator.compute_benchmark_score()

        # ---- Store trial result ----
        evaluator.add_trial_result(
            metadata={
                "cup": row["cup"],
                "grasp_type": row["grasp type"],
                "handover_location": row["handover location"],
                "fullness": row["filling (ml)"]
            },
            scores={
                "S_vision": S_vision,
                "S_robot": S_robot,
                "S_task": S_task,
                "S_benchmark": S_benchmark
            }
        )

    # -------------------------
    # Aggregated results
    # -------------------------
    agg_results = evaluator.compute_aggregated_scores()

    # -------------------------
    # Print results
    # -------------------------
    print("\n--- Overall Mean ---")
    print(agg_results["overall_mean"])
    print("\n--- Overall Std ---")
    print(agg_results["overall_std"])

    print("\n--- Per Cup Mean ---")
    print(agg_results["per_cup_mean"])
    print("\n--- Per Cup Std ---")
    print(agg_results["per_cup_std"])

    print("\n--- Per Grasp Mean ---")
    print(agg_results["per_grasp_mean"])
    print("\n--- Per Grasp Std ---")
    print(agg_results["per_grasp_std"])

    print("\n--- Per Location Mean ---")
    print(agg_results["per_location_mean"])
    print("\n--- Per Location Std ---")
    print(agg_results["per_location_std"])

    print("\n--- Per Fullness Mean ---")
    print(agg_results["per_fullness_mean"])
    print("\n--- Per Fullness Std ---")
    print(agg_results["per_fullness_std"])

    return agg_results
