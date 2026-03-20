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
#  Created Date: 2026/01/11
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
I don't know how to compute the mass of the filling. We only have the filling amount in millilitre, but to compute mass,
you need to convert it to grams. So you need to know how much the filling per ml weighs in grams. 
The ground-truths were done in white rice,
which is about 0.81g per 1ml. But the predictions could have used different rice, which could have a different weighing factor.
"""

import sys
import pandas as pd
import numpy as np
import copy

from typing import Iterable, Optional, Union

from loguru import logger

# Configure logger
logger.remove()  # Remove default handler
logger.add(sys.stderr, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                              "<level>{level: <8}</level> | "
                              "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                              "<level>{message}</level>",
           level="DEBUG")
###############################################################################

Number = Union[int, float, np.ndarray]

class CorsmalEvaluationToolkit:
    """
    CORSMAL Evaluation Toolkit core class.

    Attributes:
        n_config_cup (int): Number of configurations per cup.
        n_subjects (int): Number of subjects.
        n_cups (int): Number of cup types.
        n_configs (int): Total number of configurations.
    """

    # -------------------------
    # Default λ weights from paper (sum to 1)
    # -------------------------
    DEFAULT_LAMBDAS = {
        "delivery_location": 0.20,         # λ9
        "delivery_mass_filling": 0.20,     # λ11
        "time_human_maneuvering": 0.20,    # λ12
        "time_handover": 0.20,             # λ13
        "time_robot_maneuvering": 0.20     # λ14
    }

    # -------------------------
    # Unit normalization constants (paper assumes these units)
    # -------------------------
    UNIT_NORMALIZATION = {
        "distance_mm": 1.0,   # already in mm
        "mass_g": 1.0,        # already in grams
        "percentage": 1.0,    # already in %
        "time_s": 1.0         # already in seconds
    }

    def __init__(self, n_config_cup: int = 18, n_subjects: int = 4, n_cups: int = 4):
        self.n_config_cup = n_config_cup
        self.n_subjects = n_subjects
        self.n_cups = n_cups

        self.trial_results = []  # store per-trial results

        # Compute total configurations
        self.n_configs = self.n_config_cup * self.n_subjects * self.n_cups

        # Initialize scores
        try:
            self.reset_all_scores()
        except Exception as e:
            raise RuntimeError(f"Failed to reset scores during initialization: {e}")
        
    def reset_all_scores(self) -> None:
        """
        Reset all evaluation scores to their initial state (0.0).
        Organizes scores into Vision, Robot, Task, Group Scores, and Benchmark.
        """
        self.scores = {
            "vision": {
                "width_top": 0.0,       # mm
                "width_bottom": 0.0,    # mm
                "height": 0.0,          # mm
                "mass": 0.0,            # grams (cup + filling)
                "fullness": 0.0         # %
            },
            "robot": {
                "mass_robot": 0.0,      # grams
                "hand_pose": 0.0,       # mm / degrees
                "end_effector": 0.0     # mm / degrees
            },
            "task": {
                "delivery_location": 0.0,       # mm
                "delivery_mass_filling": 0.0,   # grams
                "time_human_maneuvering": 0.0,  # ms
                "time_handover": 0.0,           # ms
                "time_robot_maneuvering": 0.0   # ms
            },
            "group_scores": {
                "vision_score": 0.0,
                "robot_score": 0.0,
                "task_score": 0.0
            },
            "benchmark_score": 0.0
        }
    
    def add_trial_result(self, metadata: dict, scores: dict):
        """
        Store a single trial's metadata and computed scores.
        metadata: dict with keys like 'cup', 'grasp_type', 'handover_location', 'fullness'
        scores: dict with keys 'S_vision', 'S_robot', 'S_task', 'S_benchmark'
        """
        self.trial_results.append({**metadata, **scores})

    # -------------------------
    # Utility Functions
    # -------------------------
    def check_length_arrays(self, array1: Union[list, np.ndarray], array2: Union[list, np.ndarray]) -> None:
        """
        Validate that two arrays/lists have the same length.

        Args:
            array1: First array-like object.
            array2: Second array-like object.

        Raises:
            ValueError: If lengths do not match.
        """
        if len(array1) != len(array2):
            raise ValueError(
                f"Length mismatch: predictions ({len(array1)}) != annotations ({len(array2)})"
            )
    
    def check_length_preds_gts(self, preds: Iterable, gts: Iterable) -> None:
        """Alias for check_length_arrays with clearer naming."""
        self.check_length_arrays(preds, gts)
        
    def get_measure_annotations(
        df_annotations: pd.DataFrame,
        measure: str,
        n_config_cup: int,
        n_subjects: int
    ) -> np.ndarray:
        """
        Return all the annotations for a given measure as a NumPy array.

        Args:
            df_annotations: DataFrame with all the annotations.
            measure: One of ['width_at_the_top', 'width_at_the_bottom', 'height', 'volume'].
            n_config_cup: Number of configurations for each cup (default: 18).
            n_subjects: Number of subjects (default: 4).

        Returns:
            np.ndarray: Flattened array of annotations.
        """
        valid_measures = ['width_at_the_top', 'width_at_the_bottom', 'height', 'volume']
        if measure not in valid_measures:
            raise ValueError(f"Invalid measure '{measure}'. Must be one of {valid_measures}.")

        if measure == 'volume':
            if not {"cup", "filling (ml)"}.issubset(df_annotations.columns):
                raise KeyError("Missing required columns for volume calculation.")

            cups = df_annotations["cup"].to_numpy()
            fillings = df_annotations["filling (ml)"].to_numpy()

            measure_annotations = []
            for j in range(len(cups)):
                current_filling = fillings[j]
                current_cup_str = f"cup{cups[j]}"
                if current_cup_str not in df_annotations[measure]:
                    raise KeyError(f"Missing volume data for {current_cup_str}.")
                current_volume = df_annotations[measure][current_cup_str]
                gt_fullness = (current_filling / current_volume) * 100
                measure_annotations.append(gt_fullness)

            return np.array(measure_annotations, dtype=float)

        else:
            try:
                cup_arrays = [
                    np.repeat(df_annotations[measure][f"cup{i}"], n_config_cup)
                    for i in range(1, 5)
                ]
            except KeyError as e:
                raise KeyError(f"Missing expected column in annotations: {e}")

            cups_all = np.concatenate(cup_arrays)
            return np.tile(cups_all, n_subjects).astype(float)

    # -------------------------
    # Sigma Functions
    # -------------------------
    def compute_score_type_1(self, a: Number, b: Number) -> Number:
        """
        Sigma score type 1: relative difference scoring.

        Args:
            a: Predicted value(s).
            b: Ground truth value(s).

        Returns:
            Score(s) between 0 and 1.
        """
        a = np.asarray(a, dtype=float)
        b = np.asarray(b, dtype=float)

        # Handle zero-zero case
        mask_zero = (a == 0) & (b == 0)
        score = np.ones_like(a, dtype=float)

        diff_a_b = np.abs(a - b)
        mask_large_diff = diff_a_b >= np.abs(b)

        score[mask_large_diff] = 0
        mask_normal = ~mask_zero & ~mask_large_diff
        score[mask_normal] = 1 - (diff_a_b[mask_normal] / np.abs(b[mask_normal]))

        return score if score.size > 1 else float(score)

    def compute_score_type_2(self, a: Number, eta: float) -> Number:
        """
        Sigma score type 2: threshold-based scoring.

        Args:
            a: Predicted error(s).
            eta: Threshold value.

        Returns:
            Score(s) between 0 and 1.
        """
        a = np.asarray(a, dtype=float)
        score = np.where(a < eta, 1 - (a / eta), 0.0)
        return score if score.size > 1 else float(score)

    def compute_score_type_3(self, P: np.ndarray, P_hat: np.ndarray, epsilon: float) -> float:
        """
        Sigma score type 3: spatial/pose-based scoring.

        Args:
            P: Ground truth pose matrix or vector.
            P_hat: Predicted pose matrix or vector.
            epsilon: Tolerance threshold.

        Returns:
            Score between 0 and 1.
        """
        # TODO: Implement based on actual pose format
        # Placeholder: Euclidean distance scoring
        diff = np.linalg.norm(np.asarray(P) - np.asarray(P_hat))
        return 1.0 if diff <= epsilon else max(0.0, 1 - diff / epsilon)

    # -------------------------
    # Metric Computations
    # -------------------------

    def compute_width_top(self, preds: Iterable[float], gts: Iterable[float]) -> float:
        self.check_length_preds_gts(preds, gts)
        return self.compute_score_type_1(np.array(preds), np.array(gts))

    def compute_width_bottom(self, preds: Iterable[float], gts: Iterable[float]) -> float:
        self.check_length_preds_gts(preds, gts)
        return self.compute_score_type_1(np.array(preds), np.array(gts))

    def compute_height(self, preds: Iterable[float], gts: Iterable[float]) -> float:
        self.check_length_preds_gts(preds, gts)
        return self.compute_score_type_1(np.array(preds), np.array(gts))

    def compute_mass_vision(self, preds: Iterable[float], gts: Optional[Iterable[float]]) -> float:
        if gts is not None:
            self.check_length_preds_gts(preds, gts)
            return self.compute_score_type_1(np.array(preds), np.array(gts))
        return 0.0  # No GT available

    def compute_fullness(self, preds: Iterable[float], gts: Iterable[float]) -> float:
        self.check_length_preds_gts(preds, gts)
        return self.compute_score_type_1(np.array(preds), np.array(gts))

    def compute_mass_robot(self, preds: Iterable[float], gts: Iterable[float]) -> float:
        self.check_length_preds_gts(preds, gts)
        if not preds:
            raise ValueError("Empty predictions list for mass_robot computation.")
        scores = [self.compute_score_type_1(p, g) for p, g in zip(preds, gts)]
        return float(np.mean(scores))

    def compute_human_hand_pose_prediction(self, preds, gts, epsilon: float) -> float:
        return self.compute_score_type_3(preds, gts, epsilon)

    def compute_end_effector(self, preds, gts, epsilon: float) -> float:
        return self.compute_score_type_3(preds, gts, epsilon)
    
    # -------------------------
    # Task Metric Computations
    # -------------------------
    def compute_task_metric_avg_sigma2(self, preds, thr: float) -> float:
        """
        Compute the average sigma_2 score for a list of predictions.

        Args:
            preds: Iterable of prediction values.
            thr: Threshold for sigma_2 scoring.

        Returns:
            float: Average sigma_2 score.
        """
        preds = list(preds)
        if not preds:
            raise ValueError("Empty predictions list for task metric.")
        return float(np.mean([self.compute_score_type_2(p, thr) for p in preds]))
    
    def compute_delivery_location(self, preds_mm: Iterable[float], thr_mm: float) -> float:
        """s9: Delivery location error in mm."""
        preds_mm = [p / self.UNIT_NORMALIZATION["distance_mm"] for p in preds_mm]
        score = self.compute_task_metric_avg_sigma2(preds_mm, thr_mm)
        self.scores["task"]["delivery_location"] = score
        return score

    def compute_delivery_mass_filling(self, preds_g: Iterable[float], thr_g: float) -> float:
        """s11: Delivery mass filling error in grams."""
        preds_g = [p / self.UNIT_NORMALIZATION["mass_g"] for p in preds_g]
        score = self.compute_task_metric_avg_sigma2(preds_g, thr_g)
        self.scores["task"]["delivery_mass_filling"] = score
        return score

    def compute_time_human_maneuvering(self, preds_s: Iterable[float], thr_s: float) -> float:
        """s12: Time human maneuvering in seconds."""
        preds_s = [p / self.UNIT_NORMALIZATION["time_s"] for p in preds_s]
        score = self.compute_task_metric_avg_sigma2(preds_s, thr_s)
        self.scores["task"]["time_human_maneuvering"] = score
        return score

    def compute_time_handover(self, preds_s: Iterable[float], thr_s: float) -> float:
        """s13: Time handover in seconds."""
        preds_s = [p / self.UNIT_NORMALIZATION["time_s"] for p in preds_s]
        score = self.compute_task_metric_avg_sigma2(preds_s, thr_s)
        self.scores["task"]["time_handover"] = score
        return score

    def compute_time_robot_maneuvering(self, preds_s: Iterable[float], thr_s: float) -> float:
        """s14: Time robot maneuvering in seconds."""
        preds_s = [p / self.UNIT_NORMALIZATION["time_s"] for p in preds_s]
        score = self.compute_task_metric_avg_sigma2(preds_s, thr_s)
        self.scores["task"]["time_robot_maneuvering"] = score
        return score
    
    # -------------------------
    # Group Score Computations
    # -------------------------
    def compute_vision_score(self) -> float:
        v = self.scores["vision"]
        score = (
            v["width_top"] / 9 +
            v["width_bottom"] / 9 +
            v["height"] / 9 +
            v["mass"] / 3 +
            v["fullness"] / 3
        )
        self.scores["group_scores"]["vision_score"] = score
        return score

    def compute_robot_score(self) -> float:
        r = self.scores["robot"]
        score = (r["mass_robot"] + r["hand_pose"] + r["end_effector"]) / 3
        self.scores["group_scores"]["robot_score"] = score
        return score

    def compute_task_score(self, lambdas: Optional[dict] = None) -> float:
        """
        Compute the task group score.
        If lambdas are provided, use weighted sum; otherwise use DEFAULT_LAMBDAS.
        """
        t = self.scores["task"]

        # Use default lambdas if none provided
        if lambdas is None:
            lambdas = self.DEFAULT_LAMBDAS

        # Validate lambda keys
        for key in lambdas:
            if key not in t:
                raise ValueError(f"Invalid lambda key: {key}")

        # Weighted sum
        score = sum(lambdas[k] * t[k] for k in lambdas)
        self.scores["group_scores"]["task_score"] = score
        return score

    def compute_benchmark_score(self) -> float:
        g = self.scores["group_scores"]
        score = (g["vision_score"] + g["robot_score"] + g["task_score"]) / 3
        self.scores["benchmark_score"] = score
        return score

    # -------------------------
    # Evaluation Orchestration
    # -------------------------
    def run_benchmark_evaluation(self, df_pred, df_gts) -> None:
        """
        Run the benchmark evaluation by comparing predictions against ground truth.
        Stores results in self.scores.
        """
        required_columns = [
            "w^i (mm)", "w^i_b (mm)", "h^i (mm)",
            "m^i_v (grams)", "f^i (%)"
        ]
        missing_cols = [col for col in required_columns if col not in df_pred.columns]
        if missing_cols:
            raise ValueError(f"Missing required prediction columns: {missing_cols}")

        try:
            # Vision metrics
            self.scores["vision"]["width_top"] = self.compute_width_top(
                df_pred["w^i (mm)"],
                self.get_measure_annotations(df_gts, "width_at_the_top", self.n_config_cup, self.n_subjects)
            )

            self.scores["vision"]["width_bottom"] = self.compute_width_bottom(
                df_pred["w^i_b (mm)"],
                self.get_measure_annotations(df_gts, "width_at_the_bottom", self.n_config_cup, self.n_subjects)
            )

            self.scores["vision"]["height"] = self.compute_height(
                df_pred["h^i (mm)"],
                self.get_measure_annotations(df_gts, "height", self.n_config_cup, self.n_subjects)
            )

            self.scores["vision"]["mass"] = self.compute_mass_vision(
                df_pred["m^i_v (grams)"], None
            )

            self.scores["vision"]["fullness"] = self.compute_fullness(
                df_pred["f^i (%)"],
                self.get_measure_annotations(df_gts, "volume", self.n_config_cup, self.n_subjects)
            )

        except Exception as e:
            raise RuntimeError(f"Error during benchmark evaluation: {e}")
        
    def compute_aggregated_scores(self):
        """
        Compute aggregated mean and std per category (cup, grasp, location, fullness)
        Returns a dict of DataFrames.
        """
        if not self.trial_results:
            raise ValueError("No trial results to aggregate.")

        df = pd.DataFrame(self.trial_results)

        # Overall mean and std
        overall_mean = df[["S_vision", "S_robot", "S_task", "S_benchmark"]].mean()
        overall_std = df[["S_vision", "S_robot", "S_task", "S_benchmark"]].std()

        # Grouped means and stds
        per_cup_mean = df.groupby("cup")[["S_vision", "S_robot", "S_task", "S_benchmark"]].mean()
        per_cup_std = df.groupby("cup")[["S_vision", "S_robot", "S_task", "S_benchmark"]].std()

        per_grasp_mean = df.groupby("grasp_type")[["S_vision", "S_robot", "S_task", "S_benchmark"]].mean()
        per_grasp_std = df.groupby("grasp_type")[["S_vision", "S_robot", "S_task", "S_benchmark"]].std()

        per_location_mean = df.groupby("handover_location")[["S_vision", "S_robot", "S_task", "S_benchmark"]].mean()
        per_location_std = df.groupby("handover_location")[["S_vision", "S_robot", "S_task", "S_benchmark"]].std()

        per_fullness_mean = df.groupby("fullness")[["S_vision", "S_robot", "S_task", "S_benchmark"]].mean()
        per_fullness_std = df.groupby("fullness")[["S_vision", "S_robot", "S_task", "S_benchmark"]].std()

        return {
            "overall_mean": overall_mean,
            "overall_std": overall_std,
            "per_cup_mean": per_cup_mean,
            "per_cup_std": per_cup_std,
            "per_grasp_mean": per_grasp_mean,
            "per_grasp_std": per_grasp_std,
            "per_location_mean": per_location_mean,
            "per_location_std": per_location_std,
            "per_fullness_mean": per_fullness_mean,
            "per_fullness_std": per_fullness_std
        }

    # -------------------------
    # Getters
    # -------------------------

    def get_vision_score(self) -> float:
        """Return the current vision score."""
        return self.scores["group_scores"]["vision_score"]

    def get_robot_score(self) -> float:
        """Return the current robot score."""
        return self.scores["group_scores"]["robot_score"]

    def get_task_score(self) -> float:
        """Return the current task score."""
        return self.scores["group_scores"]["task_score"]

    def get_benchmark_score(self) -> float:
        """Return the current benchmark score."""
        return self.scores["benchmark_score"]
    
    def get_all_scores(self) -> dict:
        """
        Return a deep copy of all scores to prevent accidental modification.
        """
        return copy.deepcopy(self.scores)
