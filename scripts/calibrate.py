"""
calibrate.py
------------
Weight-calibration utility (project Step 9).

Compares the framework score against reference ("human") ratings and performs
a small grid search over the Model-A category weights to minimise the mean
absolute error (MAE).

Because no real human-rated benchmark ships with a student project, the
reference ratings used here are SYNTHETIC and clearly labelled: they are
produced by an independent heuristic (a simple unweighted mean of the ten
category scores). The purpose is to demonstrate the calibration *method*
and to report a genuine MAE for the shipped default weights - not to claim
an empirically validated model.

Usage:
    python scripts/calibrate.py --records 200
"""

import argparse
import itertools
import os
import random
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from backend.models.categories import DEFAULT_WEIGHTS  # noqa: E402
from backend.services.assessment_engine import calculate_privacy_risk  # noqa: E402
from backend.services.scoring_engine import calculate_overall_score  # noqa: E402
from data.generate_dataset import PERSONAS, synthetic_answers  # noqa: E402


def build_benchmark(count: int, seed: int = 11):
    """Create (category_scores, reference_rating) pairs from synthetic profiles."""
    random.seed(seed)
    names = list(PERSONAS)
    weights = [PERSONAS[n]["weight"] for n in names]
    rows = []
    for _ in range(count):
        persona = random.choices(names, weights=weights, k=1)[0]
        result = calculate_privacy_risk(synthetic_answers(PERSONAS[persona]["bias"]))
        scores = result["category_scores"]
        reference = round(statistics.mean(scores.values()), 2)   # independent heuristic
        rows.append((scores, reference))
    return rows


def mae(rows, weights):
    return round(statistics.mean(
        abs(calculate_overall_score(scores, weights) - reference) for scores, reference in rows), 3)


def grid_search(rows, deltas=(-0.03, 0.0, 0.03), tuned=("personal_information",
                                                        "location_exposure",
                                                        "account_security")):
    """Small, transparent grid search over three influential category weights."""
    best = (mae(rows, DEFAULT_WEIGHTS), dict(DEFAULT_WEIGHTS))
    for combo in itertools.product(deltas, repeat=len(tuned)):
        candidate = dict(DEFAULT_WEIGHTS)
        for key, delta in zip(tuned, combo):
            candidate[key] = max(0.01, candidate[key] + delta)
        error = mae(rows, candidate)
        if error < best[0]:
            best = (error, candidate)
    return best


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calibrate Model-A weights")
    parser.add_argument("--records", type=int, default=200)
    args = parser.parse_args()

    benchmark = build_benchmark(args.records)
    baseline = mae(benchmark, DEFAULT_WEIGHTS)
    best_error, best_weights = grid_search(benchmark)

    print(f"Benchmark profiles (synthetic reference ratings): {len(benchmark)}")
    print(f"MAE with shipped default weights : {baseline}")
    print(f"MAE after grid search            : {best_error}")
    print("Best candidate weights:")
    for key, value in best_weights.items():
        marker = "  <- changed" if abs(value - DEFAULT_WEIGHTS[key]) > 1e-9 else ""
        print(f"  {key:<22} {value:.3f}{marker}")
    print("\nNOTE: reference ratings are synthetic. The shipped defaults are NOT changed "
          "automatically; calibration against real expert ratings is future work.")
