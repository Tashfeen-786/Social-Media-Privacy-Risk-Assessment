"""
assessment_engine.py
--------------------
Orchestrates the full assessment pipeline:

    User -> Questionnaire -> Input Validation -> Feature Extraction
         -> Category Analyzers -> Category Scores (MODEL A)
         -> Risk Scoring Engine -> Overall Risk -> Risk Classification
         -> Exposure Rubric (MODEL B)
         -> Findings Engine -> Recommendation Engine
         -> Dashboard / Report / Anonymised aggregates
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

from backend.models.categories import (
    CATEGORIES,
    DISCLAIMER,
    METHODOLOGY,
    RUBRIC_CATEGORIES,
    classify_risk_level,
    load_weights,
)
from backend.models.questions import QUESTION_INDEX, QUESTIONS, valid_answers
from backend.services.exposure_rubric import calculate_exposure_rubric
from backend.services.findings_engine import generate_privacy_findings
from backend.services.recommendation_engine import generate_recommendations, priority_summary
from backend.services.scoring_engine import (
    calculate_category_scores,
    calculate_overall_score,
    explain_question_contributions,
    extract_privacy_features,
    score_breakdown,
)

# Fields that must never be accepted or stored by this application.
FORBIDDEN_FIELDS = {
    "phone", "phone_number", "mobile", "email", "email_address", "address",
    "home_address", "birthdate", "birth_date", "dob", "date_of_birth",
    "password", "passwd", "pin", "otp", "ssn", "aadhaar", "credit_card",
    "latitude", "longitude", "gps", "messages", "message_content",
    "child_name", "school_name", "full_name",
}

MIN_ANSWER_COVERAGE = 0.6  # at least 60% of the questionnaire must be answered


class ValidationError(ValueError):
    """Raised when questionnaire input fails validation."""


def validate_answers(answers: Any) -> Dict[str, str]:
    """
    Validate questionnaire input.

    Rules:
      * must be an object/dict
      * keys must be known question ids
      * values must be one of the allowed options for that question
      * rejects any attempt to submit sensitive personal data fields
      * requires a minimum answer coverage
    """
    if not isinstance(answers, dict):
        raise ValidationError("Answers must be an object of question_id -> answer.")

    cleaned: Dict[str, str] = {}
    for key, value in answers.items():
        key_str = str(key).strip()
        if key_str.lower() in FORBIDDEN_FIELDS:
            raise ValidationError(
                f"Field '{key_str}' is not accepted: this application never collects "
                f"sensitive personal data.")
        if key_str not in QUESTION_INDEX:
            raise ValidationError(f"Unknown question id: '{key_str}'.")
        if not isinstance(value, str):
            raise ValidationError(f"Answer for '{key_str}' must be a string.")
        answer = value.strip().upper()
        if len(answer) > 32:
            raise ValidationError(f"Answer for '{key_str}' is too long.")
        if answer not in valid_answers(key_str):
            raise ValidationError(
                f"Invalid answer '{value}' for question '{key_str}'. "
                f"Allowed: {', '.join(valid_answers(key_str))}.")
        cleaned[key_str] = answer

    coverage = len(cleaned) / len(QUESTIONS)
    if coverage < MIN_ANSWER_COVERAGE:
        raise ValidationError(
            f"Only {len(cleaned)} of {len(QUESTIONS)} questions answered. At least "
            f"{int(MIN_ANSWER_COVERAGE * 100)}% of the questionnaire is required.")
    return cleaned


def calculate_privacy_risk(answers: Dict[str, str],
                           weights: Dict[str, float] | None = None,
                           assessment_id: str | None = None,
                           rubric_caps: Dict[str, int] | None = None) -> Dict[str, Any]:
    """
    Full deterministic scoring pipeline (both models).

    1. validate input
    2. extract features
    3. calculate category scores (MODEL A)
    4. apply configurable weights
    5. calculate overall risk + classify level
    6. calculate the 8-category exposure rubric (MODEL B)
    7. generate findings
    8. generate recommendations
    """
    cleaned = validate_answers(answers)                                   # 1
    features = extract_privacy_features(cleaned)                          # 2
    category_scores = calculate_category_scores(features)                 # 3
    active_weights = load_weights(weights)                                # 4
    overall = calculate_overall_score(category_scores, active_weights)    # 5
    level = classify_risk_level(overall)
    rubric = calculate_exposure_rubric(cleaned, rubric_caps)              # 6
    findings = generate_privacy_findings(features)                        # 7
    recommendations = generate_recommendations(findings)                  # 8

    high_risk_categories = [
        {"category": key, "label": CATEGORIES[key], "score": score}
        for key, score in sorted(category_scores.items(), key=lambda kv: kv[1], reverse=True)
        if score >= 41
    ]

    controls = features["security_controls"]
    return {
        "assessment_id": assessment_id or f"SMPRA-{uuid.uuid4().hex[:12].upper()}",
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),

        # ---- MODEL A : privacy assessment score --------------------------
        "model_a_name": "PRIVACY ASSESSMENT SCORE",
        "overall_score": overall,
        "risk_level": level,
        "category_scores": category_scores,
        "category_labels": CATEGORIES,
        "weights_used": {k: round(v, 4) for k, v in active_weights.items()},
        "score_breakdown": score_breakdown(category_scores, active_weights),
        "top_contributors": explain_question_contributions(features)[:10],

        # ---- MODEL B : exposure rubric ------------------------------------
        "exposure_rubric": rubric,
        "rubric_labels": RUBRIC_CATEGORIES,

        # ---- shared outputs -----------------------------------------------
        "findings": findings,
        "recommendations": recommendations,
        "priority_summary": priority_summary(recommendations),
        "high_risk_categories": high_risk_categories,
        "named_features": features["named_features"],
        "security_controls": controls,
        "security_controls_enabled": sum(1 for v in controls.values() if v),
        "security_controls_total": len(controls),
        "exposure_counts": features["exposure_counts"],
        "answered_questions": features["answered_questions"],
        "total_questions": len(QUESTIONS),
        "methodology": METHODOLOGY,
        "disclaimer": DISCLAIMER,
    }


def demo_profile_answers() -> Dict[str, str]:
    """
    Safe fictional demonstration profile from the project specification.
    100% synthetic: no real person, no real account, no real data.

    Profile Public | Phone Public | Email Private | Full Birthday Public |
    Location Public | Real-Time Check-ins Yes | Travel Plans Public |
    Unknown Requests Often Accepted | Tag Review Disabled | MFA Disabled |
    Login Alerts Disabled | Third-Party Apps Not Reviewed | Old Posts Not Reviewed
    """
    return {
        "A1": "PUBLIC", "A2": "PUBLIC", "A3": "PUBLIC", "A4": "YES", "A5": "YES",
        "B1": "PUBLIC", "B2": "PRIVATE", "B3": "PUBLIC", "B4": "PUBLIC",
        "B5": "PUBLIC", "B6": "FRIENDS",
        "C1": "PUBLIC", "C2": "YES", "C3": "YES", "C4": "YES", "C5": "SOMETIMES",
        "C6": "SOMETIMES", "C7": "NO",
        "D1": "PUBLIC", "D2": "NEVER", "D3": "NO", "D4": "SOMETIMES", "D5": "SOMETIMES",
        "D6": "PUBLIC", "D7": "FRIENDS", "D8": "FRIENDS",
        "E1": "OFTEN", "E2": "NO", "E3": "NEVER", "E4": "YES", "E5": "NO",
        "F1": "NO", "F2": "YES", "F3": "PUBLIC", "F4": "YES",
        "G1": "NO", "G2": "NO", "G3": "YES", "G4": "NEVER", "G5": "NO", "G6": "NO",
        "H1": "NEVER", "H2": "YES", "H3": "NO", "H4": "NO",
        "I1": "SOMETIMES", "I2": "NO", "I3": "NO", "I4": "SOMETIMES", "I5": "NO",
        "J1": "NO", "J2": "YES", "J3": "NEVER", "J4": "YES", "J5": "YES", "J6": "YES",
        "J7": "NO", "J8": "NO",
    }


def hardened_profile_answers() -> Dict[str, str]:
    """Fully private synthetic profile - used for tests and comparisons."""
    return {q["id"]: min(q["options"], key=lambda o: o["risk"])["value"] for q in QUESTIONS}


def fully_public_answers() -> Dict[str, str]:
    """Fully public / worst-case synthetic profile - used for tests."""
    return {q["id"]: max(q["options"], key=lambda o: o["risk"])["value"] for q in QUESTIONS}


def anonymised_aggregate_record(result: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """
    Produce the privacy-minimised record that may be persisted, plus the list
    of finding types. No free text, no personal data, no raw answers.
    """
    record = {
        "assessment_id": result["assessment_id"],
        "overall_score": result["overall_score"],
        "risk_level": result["risk_level"],
        "created_at": result["created_at"],
        "exposure_score": result["exposure_rubric"]["score"],
    }
    finding_types = [f["finding_type"] for f in result["findings"]]
    return record, finding_types
