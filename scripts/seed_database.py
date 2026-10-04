"""
seed_database.py
----------------
Seeds the SQLite analytics database with privacy-minimised records generated
from SYNTHETIC questionnaire responses, so the dashboard shows meaningful
aggregate analytics out of the box.

Only scores, risk levels, finding types and timestamps are written - exactly
what a real assessment would store.
"""

import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from backend.models.database import PrivacyDatabase              # noqa: E402
from backend.services.assessment_engine import calculate_privacy_risk  # noqa: E402
from data.generate_dataset import PERSONAS, synthetic_answers    # noqa: E402


def seed(count: int = 300, seed_value: int = 7) -> int:
    random.seed(seed_value)
    db = PrivacyDatabase()
    names = list(PERSONAS)
    weights = [PERSONAS[n]["weight"] for n in names]
    for _ in range(count):
        persona = random.choices(names, weights=weights, k=1)[0]
        answers = synthetic_answers(PERSONAS[persona]["bias"])
        db.save_assessment(calculate_privacy_risk(answers))
    stats = db.dashboard_stats()
    print(f"[OK] seeded {count} synthetic assessments "
          f"(total={stats['total_assessments']}, average={stats['average_score']})")
    return count


if __name__ == "__main__":
    seed(int(sys.argv[1]) if len(sys.argv) > 1 else 300)
