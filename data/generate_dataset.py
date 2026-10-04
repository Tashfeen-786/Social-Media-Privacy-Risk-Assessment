"""
generate_dataset.py
-------------------
Generates a SYNTHETIC dataset of fictional privacy-assessment records.

ETHICAL NOTE
    Every record is randomly generated from behavioural probability profiles
    with a deterministic seed. No real person, no real account and no scraped
    data is involved. No names, e-mails, phone numbers or locations are
    generated - only privacy *configuration* attributes and the resulting
    scores of both models.

Usage:
    python data/generate_dataset.py --records 1200 --seed 42
"""

import argparse
import csv
import os
import random
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models.categories import RUBRIC_CATEGORIES  # noqa: E402
from backend.models.questions import QUESTIONS  # noqa: E402
from backend.services.assessment_engine import calculate_privacy_risk  # noqa: E402

# Behavioural archetypes -> answer-probability bias (riskiest option first)
PERSONAS = {
    "privacy_conscious": {"weight": 0.30, "bias": [0.02, 0.04, 0.16, 0.78]},
    "average_user":      {"weight": 0.42, "bias": [0.18, 0.14, 0.30, 0.38]},
    "oversharer":        {"weight": 0.28, "bias": [0.62, 0.18, 0.13, 0.07]},
}

# CSV columns (privacy configuration only - never any personal value)
FIELD_MAP = [
    ("profile_visibility", "A1"), ("friend_list_visibility", "A3"),
    ("search_engine_visible", "A4"), ("activity_status_visible", "A5"),
    ("phone_public", "B1"), ("email_public", "B2"), ("birthday_public", "B3"),
    ("workplace_public", "B4"), ("education_public", "B5"), ("relationship_public", "B6"),
    ("location_public", "C1"), ("realtime_location_sharing", "C2"),
    ("travel_posts", "C3"), ("location_tagging", "C4"), ("home_visible_photos", "C5"),
    ("live_location_sharing", "C6"), ("exif_stripped", "C7"),
    ("posts_public", "D1"), ("old_posts_reviewed", "D2"), ("document_photos", "D3"),
    ("routine_exposure", "D4"), ("workplace_media", "D5"),
    ("child_media_public", "D6"), ("child_posts_public", "D7"), ("child_school_public", "D8"),
    ("unknown_connections", "E1"), ("request_verification", "E2"), ("open_dm", "E4"),
    ("tag_review_enabled", "F1"), ("open_tagging", "F2"),
    ("mfa_enabled", "G1"), ("login_alerts_enabled", "G2"),
    ("password_reuse_reported", "G3"), ("sessions_reviewed", "G4"),
    ("third_party_apps_reviewed", "H1"), ("social_login_used", "H2"),
    ("suspicious_link_awareness", "I2"), ("otp_shared", "I3"),
    ("abandoned_accounts", "J2"), ("privacy_settings_reviewed", "J3"),
    ("handle_reuse", "J4"), ("link_aggregator", "J5"), ("linked_docs_pii", "J6"),
    ("tracker_awareness", "J7"),
]

CATEGORY_COLUMNS = [
    "profile_exposure_score", "personal_information_score", "location_exposure_score",
    "content_exposure_score", "connection_risk_score", "tagging_risk_score",
    "account_security_score", "third_party_risk_score", "social_engineering_score",
    "digital_footprint_score",
]
CATEGORY_KEYS = [
    "profile_exposure", "personal_information", "location_exposure", "content_exposure",
    "connection_risk", "tagging_risk", "account_security", "third_party_risk",
    "social_engineering", "digital_footprint",
]


def _pick(options, bias):
    """Choose an answer option using persona bias aligned to option risk order."""
    ordered = sorted(options, key=lambda o: -o["risk"])          # riskiest first
    weights = (bias + [bias[-1]] * len(ordered))[:len(ordered)]
    return random.choices(ordered, weights=weights, k=1)[0]["value"]


def synthetic_answers(persona_bias):
    return {q["id"]: _pick(q["options"], list(persona_bias)) for q in QUESTIONS}


def generate(records: int, seed: int, output: str) -> str:
    random.seed(seed)
    persona_names = list(PERSONAS)
    persona_weights = [PERSONAS[p]["weight"] for p in persona_names]
    start = datetime.now(timezone.utc) - timedelta(days=365)

    header = (["record_id", "persona", "assessment_date"]
              + [name for name, _ in FIELD_MAP]
              + CATEGORY_COLUMNS
              + [f"rubric_{key}" for key in RUBRIC_CATEGORIES]
              + ["risk_score", "risk_level", "exposure_rubric_score", "exposure_rubric_level"])

    os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)
    with open(output, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        for index in range(1, records + 1):
            persona = random.choices(persona_names, weights=persona_weights, k=1)[0]
            answers = synthetic_answers(PERSONAS[persona]["bias"])
            result = calculate_privacy_risk(answers)
            rubric = result["exposure_rubric"]
            date = (start + timedelta(minutes=random.randint(0, 525_600))).date().isoformat()
            writer.writerow(
                [f"SYN-{index:05d}", persona, date]
                + [answers[qid] for _, qid in FIELD_MAP]
                + [result["category_scores"][key] for key in CATEGORY_KEYS]
                + [rubric["category_points"][key] for key in RUBRIC_CATEGORIES]
                + [result["overall_score"], result["risk_level"],
                   rubric["score"], rubric["risk_level"]]
            )
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic privacy assessments")
    parser.add_argument("--records", type=int, default=1200)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", default=os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "social_media_privacy_assessments.csv"))
    args = parser.parse_args()
    path = generate(args.records, args.seed, args.output)
    print(f"[OK] {args.records} synthetic records written to {path}")
