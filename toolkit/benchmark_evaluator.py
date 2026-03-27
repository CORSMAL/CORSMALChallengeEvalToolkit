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

    DELIVERY_LOCATION_TH = 500 #mm

    TIMING_PARAMS = {
        "human_maneuvering": {
            "plateau_th": 1500,  # ms
            "tau": 1500,         # ms
            "epsilon": 0.05
        },
        "handover": {
            "plateau_th": 400,   # ms
            "tau": 600,          # ms
            "epsilon": 0.05
        },
        "robot_maneuvering": {
            "plateau_th": 1500,  # ms
            "tau": 1500,         # ms
            "epsilon": 0.05
        }
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

    # --------------------------------------------------
    # Scoring Functions (for each single configuration)
    # --------------------------------------------------
    def compute_score_type_1(self,
                            a: Number,
                            b: Number,
                            *,
                            flag: Optional[Union[np.ndarray, list]] = None,
                            min_value: Optional[float] = None,
                            max_value: Optional[float] = None,
                            epsilon_absolute: Optional[float] = None,
                            atol: float = 1e-10,
                            return_array: bool = False) -> Union[float, np.ndarray]:
        """
        Robust Sigma_1 (σ₁) with NaN handling for predictions and optional delivered flag.

        If a is NaN for a row, the score for that row remains NaN.
        If delivered is provided and equals 0 for a row, the score for that row is set to NaN.
        (Change the final masking to 0.0 if you prefer zeros instead of NaNs.)
        """
        # Convert to numpy arrays of float
        a = np.asarray(a, dtype=float)
        b = np.asarray(b, dtype=float)

        if a.shape != b.shape:
            raise ValueError(f"Shape mismatch: {a.shape} vs {b.shape}")

        # Validate bounds if requested (ignore NaNs in validation)
        if min_value is not None:
            if np.any(np.logical_and(~np.isnan(a), a < min_value)) or np.any(np.logical_and(~np.isnan(b), b < min_value)):
                raise ValueError(f"Values below minimum {min_value}")
        if max_value is not None:
            if np.any(np.logical_and(~np.isnan(a), a > max_value)) or np.any(np.logical_and(~np.isnan(b), b > max_value)):
                raise ValueError(f"Values exceed maximum {max_value}")

        # Normalize shapes for scalar handling
        is_scalar = (a.ndim == 0)
        a = np.atleast_1d(a)
        b = np.atleast_1d(b)

        # Prepare delivered mask if provided
        if flag is not None:
            flag_arr = np.asarray(flag)
            if flag_arr.shape != a.shape:
                raise ValueError(f"Delivered flag shape mismatch: {flag_arr.shape} vs {a.shape}")
            # treat nonzero as delivered
            delivered_mask = (flag_arr != 0)
        else:
            delivered_mask = np.ones_like(a, dtype=bool)

        # Start with NaNs where a is NaN or delivered is False
        score = np.full_like(a, np.nan, dtype=float)
        valid_mask = (~np.isnan(a)) & (~np.isnan(b)) & delivered_mask

        if not np.any(valid_mask):
            # Nothing valid: return NaNs (or scalar)
            if return_array or not is_scalar:
                return score
            else:
                return float(score.flat[0])

        # Compute on valid entries only
        diff = np.abs(a[valid_mask] - b[valid_mask])
        b_abs = np.abs(b[valid_mask])

        # Initialize valid scores to ones
        s = np.ones_like(diff, dtype=float)

        # Case 1: both zero (use atol)
        mask_zero = np.isclose(a[valid_mask], 0, atol=atol) & np.isclose(b[valid_mask], 0, atol=atol)
        s[mask_zero] = 1.0

        # Case 2: small ground truth using epsilon_absolute if provided
        if epsilon_absolute is not None:
            mask_small = ~mask_zero & (b_abs < epsilon_absolute)
            if np.any(mask_small):
                s[mask_small] = np.clip(1.0 - diff[mask_small] / epsilon_absolute, 0.0, 1.0)
            mask_normal = ~mask_zero & ~mask_small
        else:
            # large error case: |a-b| >= |b| -> score 0
            mask_large = ~mask_zero & (diff >= b_abs)
            if np.any(mask_large):
                s[mask_large] = 0.0
            mask_normal = ~mask_zero & ~mask_large

        # Case 3: normal relative error
        if np.any(mask_normal):
            with np.errstate(divide='ignore', invalid='ignore'):
                rel_error = diff[mask_normal] / b_abs[mask_normal]
                s[mask_normal] = np.clip(1.0 - rel_error, 0.0, 1.0)

        # Place computed scores back into full array
        score[valid_mask] = s

        # Optional: convert any remaining infinities or invalids to 0 (you already did this)
        # score = np.where(np.isfinite(score), score, 0.0)
        score = np.nan_to_num(score, nan=0.0, posinf=0.0, neginf=0.0)

        # Return type handling
        if return_array or not is_scalar:
            return score
        else:
            return float(score.flat[0])


    def compute_score_fullness(self,
                               a: Number, 
                               b: Number,
                               *,
                               atol: float = 1e-10,
                               return_array: bool = False) -> Union[float, np.ndarray]:
        """
        """
        # Convert and validate
        a = np.asarray(a, dtype=float)
        b = np.asarray(b, dtype=float)
        
        if a.shape != b.shape:
            raise ValueError(f"Shape mismatch: {a.shape} vs {b.shape}")

        is_scalar = (a.ndim == 0)
        a = np.atleast_1d(a)
        b = np.atleast_1d(b)
        
        # Compute scores
        score = np.ones_like(a, dtype=float)
        diff = np.abs(a - b)

        score = np.clip(1.0 - diff/100, 0, 1)

        # Case 1: Both zero
        mask_zero = np.isclose(a, 0, atol=atol) & np.isclose(b, 0, atol=atol)
        score[mask_zero] = 1.0

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

    def compute_score_type_2_plateau(self,
                                    a: Number,
                                    eta: float,
                                    plateau_th: float,
                                    epsilon: float,
                                    return_array: bool = False) -> Union[float, np.ndarray]:
        """
        Plateau + exponential decay scoring with clamp.

        Behaviour (all times in same units as inputs, e.g., ms):
        - if a <= plateau_th: score = 1.0
        - elif plateau_th < a < a_cut: score = exp(-(a - plateau_th) / eta)
        - else (a >= a_cut): score = 0.0

        where a_cut = plateau_th - eta * ln(epsilon)  (since 0 < epsilon < 1, a_cut > plateau_th)

        Args:
            a: measured time(s) (>= 0). Scalar or array-like.
            eta: decay time constant (tau). Must be > 0.
            plateau_th: plateau end a0 (>= 0).
            epsilon: small clamp level in (0,1) (e.g., 1e-3 or 0.05). Defines a_cut.
            return_array: if True always return numpy array; otherwise return scalar for scalar input.

        Returns:
            score(s) in [0,1] (float or numpy array).

        Raises:
            ValueError on invalid inputs.
        """
        # Validate numeric parameters
        if not isinstance(eta, (int, float)) or eta <= 0:
            raise ValueError(f"eta (decay constant) must be > 0, got {eta}")
        if not isinstance(plateau_th, (int, float)) or plateau_th < 0:
            raise ValueError(f"plateau_th must be >= 0, got {plateau_th}")
        if not isinstance(epsilon, (int, float)) or not (0.0 < epsilon < 1.0):
            raise ValueError(f"epsilon must be in (0,1), got {epsilon}")

        # Convert and validate a
        a_arr = np.asarray(a, dtype=float)
        # detect scalar input robustly
        is_scalar = (a_arr.ndim == 0)
        # make 1-D for vectorised ops
        a_vec = np.atleast_1d(a_arr)

        if a_vec.size == 0:
            raise ValueError("Empty predictions array")

        if np.any(np.isnan(a_vec) | np.isinf(a_vec)):
            raise ValueError("Errors contain NaN/Inf")

        if np.any(a_vec < 0):
            raise ValueError(f"Errors must be ≥ 0, got min={np.min(a_vec)}")

        # compute clamp point (a_cut)
        a_cut = plateau_th - eta * np.log(epsilon)  # a_cut > plateau_th

        # prepare output
        score = np.zeros_like(a_vec, dtype=float)

        # plateau region: full score
        mask_plateau = (a_vec <= plateau_th)
        score[mask_plateau] = 1.0

        # exponential decay region: plateau_th < a < a_cut
        mask_decay = (a_vec > plateau_th) & (a_vec < a_cut)
        if np.any(mask_decay):
            # exponential decay from plateau_th with time constant eta
            score[mask_decay] = np.exp(-(a_vec[mask_decay] - plateau_th) / eta)

        # values >= a_cut remain zero (hard clamp)
        # clip for numerical safety
        score = np.clip(score, 0.0, 1.0)

        # return scalar or array according to inputs and return_array flag
        if return_array or not is_scalar:
            return score
        else:
            return float(score[0])

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

    def compute_vision_scores(self, 
                              df_pred: Number, 
                              df_gts: Number
                              ) -> None:
        """
        """
        logger.info("Step 1: Computing vision scores..")

        logger.info("    Score 1 - Width at the top ..")
        # s1: width at the top in mm
        self.scores["vision"]["width_top"] = float(self.compute_score_type_1(
            df_pred["width_top_est_mm_vision"],
            df_gts["width_top"]
            # self.get_measure_annotations(df_gts, "width_at_the_top", self.n_config_cup, self.n_subjects)
        ).mean())

        # s2: width at the bottom in mm
        logger.info("    Score 2 - Width at the bottom ..")
        self.scores["vision"]["width_bottom"] = float(self.compute_score_type_1(
            df_pred["width_bottom_est_mm_vision"],
            df_gts["width_bottom"]
            # self.get_measure_annotations(df_gts, "width_at_the_bottom", self.n_config_cup, self.n_subjects)
        ).mean())

        # s3: height in mm
        logger.info("    Score 3 - Height ..")
        self.scores["vision"]["height"] = float(self.compute_score_type_1(
            df_pred["height_est_mm_vision"],
            df_gts["height"]
            # self.get_measure_annotations(df_gts, "height", self.n_config_cup, self.n_subjects)
        ).mean())

        # s4: mass (empty cup + filling) in g
        logger.info("    Score 4 - Mass (cup + filling) ..")
        self.scores["vision"]["mass"] = float(self.compute_score_type_1(
            df_pred["mass_full_est_g_vision"], 
            df_pred["initial_mass_measured_g"], 
            # None
        ).mean())

        # s5: fullness in %
        logger.info("    Score 5 - Fullness ..")
        self.scores["vision"]["fullness"] = float(self.compute_score_fullness(
            df_pred["fill_level_est_percent_vision"],
            df_gts["fullness"]
            # self.get_measure_annotations(df_gts, "volume", self.n_config_cup, self.n_subjects)
        ).mean())

        v = self.scores["vision"]

        logger.info("     Vision score ..")
        self.scores["group_scores"]["vision_score"] = (
            self.DEFAULT_LAMBDAS["width_top"] * v["width_top"] 
            + self.DEFAULT_LAMBDAS["width_bottom"] * v["width_bottom"] 
            + self.DEFAULT_LAMBDAS["height"] * v["height"] 
            + self.DEFAULT_LAMBDAS["mass_vision"] * v["mass"]
            + self.DEFAULT_LAMBDAS["fullness"] * v["fullness"]
        )

    def compute_robot_scores(self,
                            df_pred: Number
                            ) -> None:
        """
        """
        logger.info("Step 2: Computing robot scores ..")

        logger.info("    Score 6 - Mass (cup + filling) ..")
        r = self.scores["robot"]
        r["mass_robot"] = self.compute_score_type_1(
                df_pred["robot_mass_est_g"], 
                df_pred["initial_mass_measured_g"], 
                flag=df_pred["robot_mass_est_available"]
            ).mean()

        # TODO
        logger.info("    Score 7 - Human-trajectory ..")
        r["hand_pose"] = 0.0
        
        # TODO
        logger.info("    Score 8 - End-effector reachability ..")
        r["end_effector"] = 0.0
        # self.compute_score_type_3(preds, gts, epsilon)

        # --- weighted task score ---
        logger.info("     Robot score ..")
        lambdas = self.DEFAULT_LAMBDAS
        # Use .get with default 0 to avoid KeyError if a lambda is missing
        robot_score = (
            lambdas.get("mass_robot", 0.0) * r.get("mass_robot", np.nan)
            + lambdas.get("hand_pose", 0.0) * r.get("hand_pose", np.nan)
            + lambdas.get("end_effector", 0.0) * r.get("end_effector", np.nan)
        )

        # Store results
        self.scores.setdefault("group_scores", {})["robot_score"] = float(robot_score)

    def compute_task_scores(self,
                            df_pred: pd.DataFrame,
                            target_loc: Number) -> None:
                            # df_pred: Number, 
                            # df_gts: Number,
                            # target_loc: np.array,
                            # ) -> None:
        """
        Compute task-level scores and store them in self.scores.

        Mutates:
            self.scores["task"] and self.scores["group_scores"]["task_score"]

        Args:
            df_pred: predictions DataFrame (must contain required columns).
            target_loc: iterable of 3 floats [x, y, z].
        """
        logger.info("Step 3: Computing task scores ..")

        # Validate inputs
        if not isinstance(df_pred, pd.DataFrame):
            raise TypeError("df_pred must be a pandas DataFrame")
        if len(target_loc) != 3:
            raise ValueError("target_loc must be length 3 (x, y, z)")

        t = self.scores.setdefault("task", {})
        # t = self.scores["task"]

        # s9: delivery location score
        logger.info("    Score 9 - Delivery location ..")

        est_locs = df_pred[
            ["delivery_location_est_x_mm", "delivery_location_est_y_mm", "delivery_location_est_z_mm"]
        ].to_numpy(dtype=float)

        targ_loc = np.asarray(target_loc, dtype=float).reshape(1, 3)

        # Euclidean distance; NaNs propagate naturally
        euc_dist_delivery = np.linalg.norm(est_locs - targ_loc, axis=1)

        # Apply undelivery flag: keep distances only where undelivered == 1
        undelivered_mask = df_pred["final_mass_null_flag"].to_numpy() == 1
        euc_dist_delivery = np.where(undelivered_mask, np.nan, euc_dist_delivery)

        # compute_score_type_2 expected to return array-like per-row scores
        delivery_scores = self.compute_score_type_2(euc_dist_delivery, self.DELIVERY_LOCATION_TH)
        t["delivery_location"] = float(np.nanmean(delivery_scores)) if len(delivery_scores) > 0 else float(0)

        # --- mass score ---
        logger.info("    Score 10 - Final mass ..")
        mass_scores = self.compute_score_type_1(
            df_pred["final_mass_measured_g"].to_numpy(dtype=float),
            df_pred["initial_mass_measured_g"].to_numpy(dtype=float),
            flag=~df_pred["final_mass_null_flag"].to_numpy()
        )
        t["delivery_mass_filling"] = float(np.nanmean(mass_scores)) if len(mass_scores) > 0 else float(0)

        # --- timing scores (differences) ---
        # Use explicit to_numpy and dtype=float to avoid pandas subtraction surprises
        t_robot_first = df_pred["t_robot_first_contact_ms"].to_numpy(dtype=float)
        t_human_first = df_pred["t_human_first_contact_ms"].to_numpy(dtype=float)
        t_human_last = df_pred["t_human_last_contact_ms"].to_numpy(dtype=float)
        t_robot_last = df_pred["t_robot_last_contact_ms"].to_numpy(dtype=float)

        human_maneuvering_dur = t_robot_first - t_human_first
        handover_dur = t_human_last - t_robot_first
        robot_maneuvering_dur = t_robot_last - t_human_last

        logger.info("    Score 11 - Human maneuvring time ..")
        t["time_human_maneuvering"] = float(
            np.nanmean(self.compute_score_type_2_plateau(
                human_maneuvering_dur, 
                self.TIMING_PARAMS["human_maneuvering"]["tau"],
                plateau_th=self.TIMING_PARAMS["human_maneuvering"]["plateau_th"],
                epsilon=self.TIMING_PARAMS["human_maneuvering"]["epsilon"]
            ))
        )
        logger.info("    Score 12 - Handover time ..")
        t["time_handover"] = float(
            np.nanmean(self.compute_score_type_2_plateau(
                handover_dur, 
                self.TIMING_PARAMS["handover"]["tau"],
                plateau_th=self.TIMING_PARAMS["handover"]["plateau_th"],
                epsilon=self.TIMING_PARAMS["handover"]["epsilon"]
            ))
        )
        logger.info("    Score 13 - Robot maneuvering time ..")
        t["time_robot_maneuvering"] = float(
            np.nanmean(self.compute_score_type_2_plateau(
                robot_maneuvering_dur, 
                self.TIMING_PARAMS["robot_maneuvering"]["tau"],
                plateau_th=self.TIMING_PARAMS["robot_maneuvering"]["plateau_th"],
                epsilon=self.TIMING_PARAMS["robot_maneuvering"]["epsilon"]
            ))
        )

        # --- weighted task score ---
        logger.info("     Task score ..")
        lambdas = self.DEFAULT_LAMBDAS
        # Use .get with default 0 to avoid KeyError if a lambda is missing
        task_score = (
            lambdas.get("delivery_location", 0.0) * t.get("delivery_location", np.nan)
            + lambdas.get("delivery_mass_filling", 0.0) * t.get("delivery_mass_filling", np.nan)
            + lambdas.get("time_human_maneuvering", 0.0) * t.get("time_human_maneuvering", np.nan)
            + lambdas.get("time_handover", 0.0) * t.get("time_handover", np.nan)
            + lambdas.get("time_robot_maneuvering", 0.0) * t.get("time_robot_maneuvering", np.nan)
        )

        # Store results
        self.scores.setdefault("group_scores", {})["task_score"] = float(task_score)
    
    def compute_benchmark_score(self, weights: dict | None = None) -> float:
        """
        Compute and store the benchmark score as a weighted average of group scores.

        Args:
            weights: optional mapping of group name to weight. Defaults to equal weights
                    for 'vision_score', 'robot_score', 'task_score'.

        Returns:
            The computed benchmark score (float). Also stored in self.scores["benchmark_score"].

        Raises:
            KeyError if required group scores are missing.
            ValueError if weights are invalid (non-positive total).
        """
        logger.info("Step 4: Computing benchmark score ..")

        import math

        required = ["vision_score", "robot_score", "task_score"]
        g = self.scores.get("group_scores")
        if not isinstance(g, dict):
            raise KeyError("self.scores['group_scores'] must be a dict and present")
        
        # Ensure required keys exist
        missing = [k for k in required if k not in g]
        if missing:
            raise KeyError(f"Missing group_scores keys: {missing}")

        # Default equal weights
        if weights is None:
            weights = {k: 1.0 for k in required}
        else:
            # keep only relevant weights and fill defaults
            weights = {k: float(weights.get(k, 0.0)) for k in required}

        total_weight = sum(weights.values())
        if total_weight <= 0 or math.isclose(total_weight, 0.0):
            raise ValueError("Sum of weights must be positive")

        # Collect scores and handle NaNs by ignoring them in numerator and denominator
        scores = []
        wts = []
        for k in required:
            val = g[k]
            try:
                val = float(val)
            except Exception:
                val = float("nan")
            if not np.isnan(val):
                scores.append(val)
                wts.append(weights[k])
            else:
                # If you prefer to treat NaN as zero, replace the above with:
                # scores.append(0.0); wts.append(weights[k])
                pass

        if not scores:
            benchmark = float(0)
        else:
            # weighted average
            weighted_sum = sum(s * w for s, w in zip(scores, wts))
            weight_sum = sum(wts)
            benchmark = float(weighted_sum / weight_sum)

        self.scores["benchmark_score"] = benchmark
        return benchmark

    # -------------------------
    # Evaluation Orchestration
    # -------------------------
    def run_benchmark_evaluation(self, 
                                 df_pred: pd.DataFrame, 
                                 df_gts: pd.DataFrame,
                                 target_loc: Number
                                 ) -> None:
        """
        Run the benchmark evaluation by comparing predictions against ground truth.
        Stores results in self.scores.
        """
        # all_columns = [
        #     "config_id", "robot_initial_pose_x", "robot_initial_pose_y", "robot_initial_pose_z", 
        #     "robot_initial_pose_q1", "robot_initial_pose_q2", "robot_initial_pose_q3", 
        #     "robot_initial_pose_q4", "initial_mass_measured_g", "width_top_est_mm_vision", 
        #     "width_bottom_est_mm_vision", "height_est_mm_vision", "geometry_est_timepoint",
        #     "mass_full_est_g_vision", "mass_full_est_vision_timepoint", "fill_level_est_percent_vision",
        #     "fill_level_vision_timepoint", "spill_observed_during_human_maneuvering", 
        #     "robot_mass_est_available", "robot_mass_est_g", "robot_mass_est_timepoint", 
        #     "delivery_location_est_x_mm", "delivery_location_est_y_mm", "delivery_location_est_z_mm",
        #     "final_mass_null_flag", "final_mass_measured_g", "t_human_first_contact_ms", 
        #     "t_human_last_contact_ms", "t_robot_first_contact_ms", "t_robot_last_contact_ms"
        # ]
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
            self.compute_vision_scores(df_pred, df_gts)

            # Robot metrics
            self.compute_robot_scores(df_pred)

            # Task metrics
            self.compute_task_scores(df_pred, target_loc)

            self.compute_benchmark_score()
            
        except Exception as e:
            raise RuntimeError(f"Error during benchmark evaluation: {e}")
        

        print(self.scores)

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

