#!/usr/bin/env python
"""
CORSMAL Benchmark Evaluation Toolkit

Implements performance scoring for human-to-robot handover benchmarks as specified in:
    Sanchez-Matilla et al. (2020). "Benchmark for Human-to-Robot Handovers of Unseen 
    Containers with Unknown Filling." IEEE Robotics and Automation Letters, 5(2), 1642-1649.

Performance Measures:
    Vision (S_vision): s1-s5 (geometric and fullness estimation)
    Robot (S_robot): s6-s8 (mass, hand pose, end-effector estimation)
    Task (S_task): s9, s11-s14 (delivery location, mass, time metrics)
    Benchmark (S_benchmark): Overall score = (S_vision + S_robot + S_task) / 3

Scoring Functions:
    σ₁: Relative difference scoring (0 to 1, where 1 = exact match)
    σ₂: Threshold-based scoring (penalizes errors > threshold)
    σ₃: Pose-based scoring (6D position + orientation)

Usage:
    evaluator = CorsmalEvaluationToolkit(n_config_cup=18, n_subjects=4)
    evaluator.compute_width_top(predictions, ground_truths)
    # ... more metrics ...
    S_vision = evaluator.compute_vision_score()
    S_benchmark = evaluator.compute_benchmark_score()
"""
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

FILLING_DENSITY = {
       "rice": 0.81,      # grams per mL
       "pasta": 0.75,     # estimated
       "water": 1.0,      # grams per mL
   }

# CORSMAL benchmark thresholds (from paper)
DELIVERY_LOCATION_THRESHOLD_MM = 50.0      # Distance from target
DELIVERY_MASS_THRESHOLD_G = 50.0           # Mass tolerance
# TIME_HUMAN_MANEUVERING_THRESHOLD_S = 10.0
# TIME_HANDOVER_THRESHOLD_S = 5.0
# TIME_ROBOT_MANEUVERING_THRESHOLD_S = 15.0


TIMING_PARAMS = {
    "human_maneuvring" : {
        "plateau_th": 1500, # ms
        "tau": 1500, # ms
        "epsilon": 0.05
    },
    "handover" : {
        "plateau_th": 400, # ms
        "tau": 600, # ms
        "epsilon": 0.05
    },
    "robot_maneuvring" : {
        "plateau_th": 1500, # ms
        "tau": 1500, # ms
        "epsilon": 0
    }
}

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
    # Paper indices 1-13 map to code indices 0-12
    # -------------------------
    DEFAULT_LAMBDAS = {
        "width_top": 1/9,                      # λ1 (index 0)
        "width_bottom": 1/9,                   # λ2 (index 1)
        "height": 1/9,                         # λ3 (index 2)
        "mass_vision": 1/3,                    # λ4 (index 3)
        "fullness": 1/3,                       # λ5 (index 4)
        "mass_robot": 1/3,                     # λ6 (index 5)
        "hand_pose": 1/3,                      # λ7 (index 6)
        "end_effector": 1/3,                   # λ8 (index 7)
        "delivery_location": 1/3,              # λ9 (index 8)
        "delivery_mass_filling": 1/3,          # λ10 (index 9)
        "time_human_maneuvering": 1/12,        # λ11 (index 10)
        "time_handover": 1/6,                  # λ12 (index 11)
        "time_robot_maneuvering": 1/12         # λ13 (index 12)
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
        self, 
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
    def compute_score_type_1(self, 
                        a: Number, 
                        b: Number,
                        *,
                        min_value: Optional[float] = None,
                        max_value: Optional[float] = None,
                        epsilon_absolute: Optional[float] = None,
                        atol: float = 1e-10,
                        return_array: bool = False) -> Union[float, np.ndarray]:
        """
        Sigma_1 (σ₁): Relative difference scoring.

        Used for: s1-s5 (width_top, width_bottom, height, mass_vision, fullness)
    
        Formula:
            σ₁(a, b) = {
                1.0,              if a=0 ∧ b=0  (perfect match) [only for fullness]
                0.0,              if |a-b| ≥ |b|  (100%+ error)
                1 - |a-b|/|b|,    otherwise (relative error)
            }
        
        Args:
            a: Predicted value(s)
            b: Ground truth value(s)
            min_value: Validate all values >= min_value
            max_value: Validate all values <= max_value
            epsilon_absolute: If provided, use absolute tolerance for |b| < epsilon_absolute
            atol: Absolute tolerance for zero comparisons
            return_array: If True, always return array; else return float for scalar input
        
        Returns:
            Score in [0, 1]
        """
        # Convert and validate
        a = np.asarray(a, dtype=float)
        b = np.asarray(b, dtype=float)
        
        if a.shape != b.shape:
            raise ValueError(f"Shape mismatch: {a.shape} vs {b.shape}")
        
        if min_value is not None and (np.any(a < min_value) or np.any(b < min_value)):
            raise ValueError(f"Values below minimum {min_value}")
        
        if max_value is not None and (np.any(a > max_value) or np.any(b > max_value)):
            raise ValueError(f"Values exceed maximum {max_value}")
        
        is_scalar = (a.ndim == 0)
        a = np.atleast_1d(a)
        b = np.atleast_1d(b)
        
        # Compute scores
        score = np.ones_like(a, dtype=float)
        diff = np.abs(a - b)
        b_abs = np.abs(b)
        
        # Case 1: Both zero
        mask_zero = np.isclose(a, 0, atol=atol) & np.isclose(b, 0, atol=atol)
        score[mask_zero] = 1.0
        
        # Case 2: Small ground truth (use absolute tolerance if provided)
        if epsilon_absolute is not None:
            mask_small = ~mask_zero & (b_abs < epsilon_absolute)
            score[mask_small] = np.clip(1.0 - diff[mask_small] / epsilon_absolute, 0, 1)
            mask_normal = ~mask_zero & ~mask_small
        else:
            # Original: large error case
            mask_large = ~mask_zero & (diff >= b_abs)
            score[mask_large] = 0.0
            mask_normal = ~mask_zero & ~mask_large
        
        # Case 3: Normal relative error
        with np.errstate(divide='ignore', invalid='ignore'):
            if np.any(mask_normal):
                rel_error = diff[mask_normal] / b_abs[mask_normal]
                score[mask_normal] = np.clip(1.0 - rel_error, 0, 1)
        
        score = np.nan_to_num(score, nan=0.0, posinf=0.0, neginf=0.0)
        
        # Return type
        if return_array or not is_scalar:
            return score
        else:
            return float(score.flat[0])

    def compute_score_type_2(self, a: Number, eta: float,
                        return_array: bool = False) -> Union[float, np.ndarray]:
        """
        Sigma_2 (σ₂): Threshold-based scoring.
        
        σ₂(a, η) = { 1 - a/η,  if a < η
                    { 0.0,      if a ≥ η
        
        Args:
            a: Predicted error(s). Must be ≥ 0.
            eta: Threshold value. Must be > 0.
            return_array: If True, always return array; else float for scalar.
        
        Returns:
            Score(s) in [0, 1].
        
        Raises:
            ValueError: If eta ≤ 0, a < 0, or a is empty.
        """
        # Validate threshold
        if not isinstance(eta, (int, float)) or eta <= 0:
            raise ValueError(f"Threshold eta must be > 0, got {eta}")
        
        # Convert and validate errors
        a = np.asarray(a, dtype=float)
        
        if a.size == 0:
            raise ValueError("Empty predictions array")
        
        if np.any(a < 0):
            raise ValueError(f"Errors must be ≥ 0, got min={np.min(a)}")
        
        if np.any(np.isinf(a) | np.isnan(a)):
            raise ValueError("Errors contain NaN/Inf")
        
        # Remember scalar input
        is_scalar = (a.ndim == 0)
        a = np.atleast_1d(a)
        
        # Compute scores
        score = np.where(a < eta, 1 - (a / eta), 0.0)
        score = np.clip(score, 0.0, 1.0)
        
        # Return type
        if return_array or not is_scalar:
            return score
        else:
            return float(score.flat[0])

    def compute_score_type_2_smooth(self, a: Number, eta: float,
                                transition_width: float = 0.1) -> Union[float, np.ndarray]:
        """
        Sigma_2 with smooth transition around threshold (reduces hard boundary).
        """
        if eta <= 0:
            raise ValueError(f"Threshold eta must be > 0")
        
        a = np.asarray(a, dtype=float)
        if np.any(a < 0):
            raise ValueError(f"Errors must be ≥ 0")
        if transition_width <= 0 or transition_width >= 1:
            raise ValueError(f"transition_width must be in (0, 1)")
        
        is_scalar = (a.ndim == 0)
        a = np.atleast_1d(a)
        
        eta_lower = eta * (1 - transition_width)
        eta_upper = eta * (1 + transition_width)
        
        score = np.ones_like(a, dtype=float)
        
        # Linear region
        mask_linear = a < eta_lower
        score[mask_linear] = 1 - (a[mask_linear] / eta)
        
        # Transition region (cubic smoothing)
        mask_trans = (a >= eta_lower) & (a <= eta_upper)
        if np.any(mask_trans):
            t = (a[mask_trans] - eta_lower) / (eta_upper - eta_lower)
            score[mask_trans] = 1 - (3*t**2 - 2*t**3)
        
        # Zero region
        mask_zero = a > eta_upper
        score[mask_zero] = 0.0
        
        score = np.clip(score, 0.0, 1.0)
        
        if is_scalar:
            return float(score.flat[0])
        else:
            return score

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
    
    def compute_score_type_3_6d(self, P_gt, P_pred, epsilon_pos_mm, epsilon_rot_deg):
        """
        Compute sigma_3 for 6D pose (position + orientation).
        
        Args:
            P_gt: Ground truth pose (position_mm: 3D, orientation: 3x3 rotation matrix)
            P_pred: Predicted pose (same format)
            epsilon_pos_mm: Position tolerance in mm
            epsilon_rot_deg: Rotation tolerance in degrees
        
        Returns:
            Score between 0 and 1
        """
        # Extract position error
        pos_gt = np.array(P_gt[:3])
        pos_pred = np.array(P_pred[:3])
        pos_error = np.linalg.norm(pos_gt - pos_pred)
        
        # Compute rotation error (use geodesic distance on SO(3))
        R_gt = np.array(P_gt[3:]).reshape(3, 3)
        R_pred = np.array(P_pred[3:]).reshape(3, 3)
        R_rel = R_gt.T @ R_pred
        # Angle from rotation matrix: θ = arccos((trace(R) - 1) / 2)
        trace = np.trace(R_rel)
        rot_error_rad = np.arccos(np.clip((trace - 1) / 2, -1, 1))
        rot_error_deg = np.degrees(rot_error_rad)
        
        # Weighted combination
        pos_score = max(0.0, 1 - (pos_error / epsilon_pos_mm))
        rot_score = max(0.0, 1 - (rot_error_deg / epsilon_rot_deg))
        return (pos_score + rot_score) / 2.0

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
        """s6: Compute score for robot mass estimation."""
        preds = list(preds)
        gts = list(gts)
        
        # Check empty FIRST before checking length
        if not preds:
            raise ValueError("Empty predictions list for mass_robot computation.")
        if not gts:
            raise ValueError("Empty ground truth list for mass_robot computation.")
        
        # Then check lengths match
        self.check_length_preds_gts(preds, gts)
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
        """
        Compute vision score as weighted combination of geometric and fullness metrics.
        
        Paper: Sanchez-Matilla et al., RA-L 2020
        Weights: Geometric (width_top, width_bottom, height) each 1/9
                Physical properties (mass, fullness) each 1/3
        Formula: S_vision = (1/9)(s1 + s2 + s3) + (1/3)(s4 + s5)
        """
        v = self.scores["vision"]
        geometric_score = (v["width_top"] + v["width_bottom"] + v["height"]) / 9
        physical_score = (v["mass"] + v["fullness"]) / 3
        vision_score = geometric_score + physical_score
        self.scores["group_scores"]["vision_score"] = vision_score
        return vision_score

    def compute_robot_score(self) -> float:
        r = self.scores["robot"]
        score = (r["mass_robot"] + r["hand_pose"] + r["end_effector"]) / 3
        self.scores["group_scores"]["robot_score"] = score
        return score

    def compute_task_score(self, lambdas: Optional[Union[dict, list]] = None) -> float:
        """Compute task score from 5 task metrics only."""
        t = self.scores["task"]
        
        if lambdas is None:
            lambdas = {"delivery_location": 0.2, "delivery_mass_filling": 0.2,
                    "time_human_maneuvering": 0.2, "time_handover": 0.2,
                    "time_robot_maneuvering": 0.2}
        
        if isinstance(lambdas, list):
            if len(lambdas) != 5:
                raise ValueError("List lambdas must have exactly 5 elements")
            lambdas = {"delivery_location": lambdas[0], "delivery_mass_filling": lambdas[1],
                    "time_human_maneuvering": lambdas[2], "time_handover": lambdas[3],
                    "time_robot_maneuvering": lambdas[4]}
        
        for key in lambdas:
            if key not in t:
                raise ValueError(f"Invalid lambda key: {key}")
        
        score = sum(lambdas[k] * t[k] for k in lambdas)
        self.scores["group_scores"]["task_score"] = float(score)
        return float(score)

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
        # required_columns = [
        #     "w^i (mm)", "w^i_b (mm)", "h^i (mm)",
        #     "m^i_v (grams)", "f^i (%)"
        # ]
        all_columns = [
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
        required_columns = [
            "initial_mass_measured_g", "width_top_est_mm_vision", 
            "width_bottom_est_mm_vision", "height_est_mm_vision", 
            "mass_full_est_g_vision", "fill_level_est_percent_vision",
            "robot_mass_est_available", "robot_mass_est_g", 
            "delivery_location_est_x_mm", "delivery_location_est_y_mm", "delivery_location_est_z_mm",
            "final_mass_null_flag", "final_mass_measured_g", "t_human_first_contact_ms", 
            "t_human_last_contact_ms", "t_robot_first_contact_ms", "t_robot_last_contact_ms"
        ]
        missing_cols = [col for col in required_columns if col not in df_pred.columns]
        if missing_cols:
            raise ValueError(f"Missing required prediction columns: {missing_cols}")

        try:
            # Vision metrics
            self.scores["vision"]["width_top"] = self.compute_width_top(
                df_pred["width_top_est_mm_vision"],
                df_gts["width_top"]
                # self.get_measure_annotations(df_gts, "width_at_the_top", self.n_config_cup, self.n_subjects)
            )

            self.scores["vision"]["width_bottom"] = self.compute_width_bottom(
                df_pred["width_bottom_est_mm_vision"],
                df_gts["width_bottom"]
                # self.get_measure_annotations(df_gts, "width_at_the_bottom", self.n_config_cup, self.n_subjects)
            )

            self.scores["vision"]["height"] = self.compute_height(
                df_pred["height_est_mm_vision"],
                df_gts["height"]
                # self.get_measure_annotations(df_gts, "height", self.n_config_cup, self.n_subjects)
            )

            self.scores["vision"]["mass"] = self.compute_mass_vision(
                df_pred["mass_full_est_g_vision"], 
                df_pred["initial_mass_measured_g"], 
                # None
            )

            self.scores["vision"]["fullness"] = self.compute_fullness(
                df_pred["fill_level_est_percent_vision"],
                df_gts["fullness"]
                # self.get_measure_annotations(df_gts, "volume", self.n_config_cup, self.n_subjects)
            )

            # Robot metrics
            self.scores["robot"]["mass"] = self.compute_mass_vision(
                df_pred["robot_mass_est_g"], 
                df_pred["initial_mass_measured_g"], 
                # None
            )

            # Task metrics
            self.scores["task"]["mass"] = self.compute_mass_vision(
                df_pred["final_mass_measured_g"], 
                df_pred["initial_mass_measured_g"], 
                # None
            )

            self.scores["task"]["time_human_maneuvering"] = self.compute_time_human_maneuvering(
                df_pred["t_robot_first_contact_ms"] - df_pred["t_human_first_contact_ms"],
                TIMING_PARAMS["human_maneuvering"]["tau"]
            )

            self.scores["task"]["time_handover"] = self.compute_time_handover(
                df_pred["t_human_last_contact_ms"] - df_pred["t_robot_first_contact_ms"],
                TIMING_PARAMS["handover"]["tau"]
            )

            self.scores["task"]["time_robot_maneuvering"] = self.compute_time_robot_maneuvering(
                df_pred["t_robot_last_contact_ms"] - df_pred["t_human_last_contact_ms"],
                TIMING_PARAMS["robot_maneuvering"]["tau"]
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

