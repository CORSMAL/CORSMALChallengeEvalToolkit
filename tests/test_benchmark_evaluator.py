import pytest
import numpy as np
import pandas as pd
from corsmal_toolkit.benchmark_evaluator import CorsmalEvaluationToolkit as BenchmarkEvaluator


@pytest.fixture
def evaluator():
    # Minimal init for testing
    e = BenchmarkEvaluator(n_config_cup=2, n_subjects=1)
    # Ensure scores dict has required structure
    e.scores = {
        "task": {
            "delivery_location": 0.0,
            "delivery_mass_filling": 0.0,
            "time_human_maneuvering": 0.0,
            "time_handover": 0.0,
            "time_robot_maneuvering": 0.0
        },
        "group_scores": {}
    }
    return e

# -------------------------
# 1. Test reset_all_scores
# -------------------------
def test_reset_all_scores_structure(evaluator):
    evaluator.reset_all_scores()
    scores = evaluator.get_all_scores()

    assert "vision" in scores
    assert "robot" in scores
    assert "task" in scores
    assert "group_scores" in scores
    assert "benchmark_score" in scores

    def check_all_zero(d):
        for v in d.values():
            if isinstance(v, dict):
                check_all_zero(v)
            else:
                assert v == 0.0
    check_all_zero(scores)

# -------------------------
# 2. Test sigma functions
# -------------------------
def test_compute_score_type_1_exact_match(evaluator):
    assert evaluator.compute_score_type_1(10, 10) == 1.0

def test_compute_score_type_1_large_diff(evaluator):
    assert evaluator.compute_score_type_1(20, 10) == 0.0

def test_compute_score_type_2_below_threshold(evaluator):
    assert evaluator.compute_score_type_2(2, 4) == 0.5

def test_compute_score_type_2_above_threshold(evaluator):
    assert evaluator.compute_score_type_2(5, 4) == 0.0

def test_compute_score_type_3_within_epsilon(evaluator):
    P = np.array([0, 0])
    P_hat = np.array([0.1, 0.1])
    assert evaluator.compute_score_type_3(P, P_hat, epsilon=1.0) == 1.0

def test_compute_score_type_3_outside_epsilon(evaluator):
    P = np.array([0, 0])
    P_hat = np.array([2, 0])
    score = evaluator.compute_score_type_3(P, P_hat, epsilon=1.0)
    assert 0.0 <= score < 1.0

# -------------------------
# 3. Test metric computations
# -------------------------
def test_compute_width_top(evaluator):
    preds = [10, 20]
    gts = [10, 20]
    score = evaluator.compute_width_top(preds, gts)
    assert np.allclose(score, [1.0, 1.0])

def test_compute_mass_robot(evaluator):
    preds = [10, 20]
    gts = [10, 30]
    score = evaluator.compute_mass_robot(preds, gts)
    assert isinstance(score, float)

# -------------------------
# 4. Test run_benchmark_evaluation
# -------------------------
def test_run_benchmark_evaluation(evaluator):
    df_pred = pd.DataFrame({
        "w^i (mm)": [10, 20, 30, 40],
        "w^i_b (mm)": [10, 20, 30, 40],
        "h^i (mm)": [10, 20, 30, 40],
        "m^i_v (grams)": [5, 5, 5, 5],
        "f^i (%)": [50, 60, 70, 80]
    })

    df_gts = pd.DataFrame({
        "cup": [1, 2, 3, 4],
        "filling (ml)": [100, 200, 300, 400],
        "width_at_the_top": {
            "cup1": 10, "cup2": 20, "cup3": 30, "cup4": 40
        },
        "width_at_the_bottom": {
            "cup1": 10, "cup2": 20, "cup3": 30, "cup4": 40
        },
        "height": {
            "cup1": 10, "cup2": 20, "cup3": 30, "cup4": 40
        },
        "volume": {
            "cup1": 200, "cup2": 400, "cup3": 600, "cup4": 800
        }
    })

    evaluator.run_benchmark_evaluation(df_pred, df_gts)
    vision_scores = evaluator.scores["vision"]
    for key, value in vision_scores.items():
        assert isinstance(value, (float, np.ndarray))

# -------------------------
# 5. Test group score computations
# -------------------------
def test_group_score_computations(evaluator):
    # Manually set some scores
    evaluator.scores["vision"] = {
        "width_top": 0.9,
        "width_bottom": 0.9,
        "height": 0.9,
        "mass": 0.8,
        "fullness": 0.7
    }
    evaluator.scores["robot"] = {
        "mass_robot": 0.6,
        "hand_pose": 0.5,
        "end_effector": 0.4
    }
    evaluator.scores["task"] = {
        "delivery_location": 0.8,
        "delivery_mass_filling": 0.7,
        "time_human_maneuvering": 0.6,
        "time_handover": 0.5,
        "time_robot_maneuvering": 0.4
    }

    vision_score = evaluator.compute_vision_score()
    robot_score = evaluator.compute_robot_score()
    task_score = evaluator.compute_task_score()
    benchmark_score = evaluator.compute_benchmark_score()

    # Check types
    assert isinstance(vision_score, float)
    assert isinstance(robot_score, float)
    assert isinstance(task_score, float)
    assert isinstance(benchmark_score, float)

    # Check that scores are stored in the dictionary
    assert evaluator.get_vision_score() == vision_score
    assert evaluator.get_robot_score() == robot_score
    assert evaluator.get_task_score() == task_score
    assert evaluator.get_benchmark_score() == benchmark_score

    # Check benchmark score is average of group scores
    expected_benchmark = (vision_score + robot_score + task_score) / 3
    assert np.isclose(benchmark_score, expected_benchmark)

# -------------------------
# 6. Edge case tests
# -------------------------
def test_empty_predictions_mass_robot(evaluator):
    with pytest.raises(ValueError, match="Empty predictions list"):
        evaluator.compute_mass_robot([], [1, 2, 3])

def test_mismatched_lengths_width_top(evaluator):
    preds = [10, 20]
    gts = [10]  # shorter
    with pytest.raises(ValueError, match="Length mismatch"):
        evaluator.compute_width_top(preds, gts)

def test_invalid_measure_name(evaluator):
    df_gts = pd.DataFrame()
    with pytest.raises(ValueError, match="Invalid measure"):
        evaluator.get_measure_annotations(df_gts, "invalid_measure", 2, 1)

def test_missing_prediction_columns(evaluator):
    df_pred = pd.DataFrame({"w^i (mm)": [10, 20]})  # missing required columns
    df_gts = pd.DataFrame()
    with pytest.raises(ValueError, match="Missing required prediction columns"):
        evaluator.run_benchmark_evaluation(df_pred, df_gts)

# -------------------------
# 7. Test compute_task_metric_avg_sigma2
# -------------------------
def test_compute_task_metric_avg_sigma2_basic(evaluator):
    preds = [1.0, 2.0, 3.0]
    thr = 4.0
    score = evaluator.compute_task_metric_avg_sigma2(preds, thr)
    # Expected: sigma_2(1,4)=0.75, sigma_2(2,4)=0.5, sigma_2(3,4)=0.25 → avg=0.5
    expected = np.mean([1 - (1/4), 1 - (2/4), 1 - (3/4)])
    assert np.isclose(score, expected)
    assert isinstance(score, float)

def test_compute_task_metric_avg_sigma2_empty(evaluator):
    with pytest.raises(ValueError, match="Empty predictions list"):
        evaluator.compute_task_metric_avg_sigma2([], 4.0)

# -------------------------
# 8. Test compute_task_score with lambdas
# -------------------------
def test_compute_task_score_with_lambdas(evaluator):
    # Set known task scores
    evaluator.scores["task"] = {
        "delivery_location": 0.9,
        "delivery_mass_filling": 0.8,
        "time_human_maneuvering": 0.7,
        "time_handover": 0.6,
        "time_robot_maneuvering": 0.5
    }
    lambdas = [0.0] * 13
    lambdas[8] = 0.25
    lambdas[10] = 0.25
    lambdas[11] = 0.25
    lambdas[12] = 0.25

    score = evaluator.compute_task_score(lambdas=lambdas)
    expected = (
        lambdas[8] * 0.9 +
        lambdas[10] * 0.8 +
        lambdas[11] * 0.7 +
        lambdas[12] * 0.6
    )
    assert np.isclose(score, expected)
    assert evaluator.get_task_score() == score

def test_compute_task_score_with_short_lambdas(evaluator):
    evaluator.scores["task"] = {
        "delivery_location": 0.9,
        "delivery_mass_filling": 0.8,
        "time_human_maneuvering": 0.7,
        "time_handover": 0.6,
        "time_robot_maneuvering": 0.5
    }
    with pytest.raises(ValueError, match="Lambdas list must have at least 13 elements"):
        evaluator.compute_task_score(lambdas=[0.1] * 5)

# -------------------------
# 9. Test compute_task_score without lambdas (simple average)
# -------------------------
def test_compute_task_score_without_lambdas(evaluator):
    evaluator.scores["task"] = {
        "delivery_location": 1.0,
        "delivery_mass_filling": 0.0,
        "time_human_maneuvering": 1.0,
        "time_handover": 0.0,
        "time_robot_maneuvering": 1.0
    }
    score = evaluator.compute_task_score()
    expected = np.mean(list(evaluator.scores["task"].values()))
    assert np.isclose(score, expected)
    assert evaluator.get_task_score() == score

# -------------------------
# σ2 scoring helper
# -------------------------
def sigma2(pred, thr):
    return max(0.0, 1.0 - (pred / thr))

# -------------------------
# Test each task metric computation
# -------------------------
def test_compute_delivery_location(evaluator):
    preds = [5.0, 10.0, 15.0]  # mm
    thr = 50.0
    expected = np.mean([sigma2(p, thr) for p in preds])
    score = evaluator.compute_delivery_location(preds, thr)
    assert np.isclose(score, expected)
    assert evaluator.scores["task"]["delivery_location"] == score

def test_compute_delivery_mass_filling(evaluator):
    preds = [10.0, 20.0, 30.0]  # grams
    thr = 50.0
    expected = np.mean([sigma2(p, thr) for p in preds])
    score = evaluator.compute_delivery_mass_filling(preds, thr)
    assert np.isclose(score, expected)
    assert evaluator.scores["task"]["delivery_mass_filling"] == score

def test_compute_time_human_maneuvering(evaluator):
    preds = [2.0, 3.0, 4.0]  # seconds
    thr = 10.0
    expected = np.mean([sigma2(p, thr) for p in preds])
    score = evaluator.compute_time_human_maneuvering(preds, thr)
    assert np.isclose(score, expected)
    assert evaluator.scores["task"]["time_human_maneuvering"] == score

def test_compute_time_handover(evaluator):
    preds = [1.0, 1.5, 2.0]  # seconds
    thr = 5.0
    expected = np.mean([sigma2(p, thr) for p in preds])
    score = evaluator.compute_time_handover(preds, thr)
    assert np.isclose(score, expected)
    assert evaluator.scores["task"]["time_handover"] == score

def test_compute_time_robot_maneuvering(evaluator):
    preds = [4.0, 5.0, 6.0]  # seconds
    thr = 15.0
    expected = np.mean([sigma2(p, thr) for p in preds])
    score = evaluator.compute_time_robot_maneuvering(preds, thr)
    assert np.isclose(score, expected)
    assert evaluator.scores["task"]["time_robot_maneuvering"] == score

# -------------------------
# Test task score computation
# -------------------------
def test_compute_task_score_default_lambdas(evaluator):
    # Set known scores
    evaluator.scores["task"] = {
        "delivery_location": 0.9,
        "delivery_mass_filling": 0.8,
        "time_human_maneuvering": 0.7,
        "time_handover": 0.6,
        "time_robot_maneuvering": 0.5
    }
    # Default lambdas are equal weights (0.2 each)
    expected = np.mean(list(evaluator.scores["task"].values()))
    score = evaluator.compute_task_score()
    assert np.isclose(score, expected)
    assert evaluator.scores["group_scores"]["task_score"] == score

def test_compute_task_score_custom_lambdas(evaluator):
    evaluator.scores["task"] = {
        "delivery_location": 1.0,
        "delivery_mass_filling": 0.0,
        "time_human_maneuvering": 0.0,
        "time_handover": 0.0,
        "time_robot_maneuvering": 0.0
    }
    lambdas = {
        "delivery_location": 1.0,
        "delivery_mass_filling": 0.0,
        "time_human_maneuvering": 0.0,
        "time_handover": 0.0,
        "time_robot_maneuvering": 0.0
    }
    score = evaluator.compute_task_score(lambdas=lambdas)
    assert np.isclose(score, 1.0)

def test_compute_task_score_invalid_lambda_key(evaluator):
    with pytest.raises(ValueError, match="Invalid lambda key"):
        evaluator.compute_task_score(lambdas={"invalid_metric": 1.0})

# -------------------------
# Test unit normalization
# -------------------------
def test_unit_normalization_distance(evaluator):
    evaluator.UNIT_NORMALIZATION["distance_mm"] = 10.0  # input in cm
    preds_cm = [0.5, 1.0, 1.5]  # cm
    thr_mm = 50.0
    # Convert cm to mm inside method
    expected_preds_mm = [p / 10.0 for p in preds_cm]
    expected = np.mean([sigma2(p, thr_mm) for p in expected_preds_mm])
    score = evaluator.compute_delivery_location(preds_cm, thr_mm)
    assert np.isclose(score, expected)
