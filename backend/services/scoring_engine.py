"""
scoring_engine.py
-----------------
MODEL A - deterministic, explainable 10-category privacy scoring.

Pipeline:
    validated answers -> extract_privacy_features()
                      -> calculate_category_scores()
                      -> apply configurable weights
                      -> overall 0-100 risk score -> risk level

There is no machine-learning black box: every point can be traced back to a
specific questionnaire answer and its documented weight.
"""

from typing import Any, Dict, List

from backend.models.categories import (
    CATEGORIES,
    DISCLAIMER,
    classify_risk_level,
    load_weights,
)
from backend.models.questions import QUESTION_INDEX, QUESTIONS, risk_value


# --------------------------------------------------------------------------
# 1. Feature engineering
# --------------------------------------------------------------------------
def extract_privacy_features(answers: Dict[str, str]) -> Dict[str, Any]:
    """
    Convert questionnaire responses into structured numerical privacy features.

    Returns:
        question_risk   : {question_id: risk 0..1}
        category_raw    : {category: weighted raw risk 0..1}
        flags           : {finding_type: bool}  (risky condition detected)
        named_features  : the explicitly required named feature flags
        security_controls / exposure_counts : dashboard aggregates
    """
    question_risk: Dict[str, float] = {}
    flags: Dict[str, bool] = {}
    category_weighted: Dict[str, float] = {key: 0.0 for key in CATEGORIES}
    category_weight_sum: Dict[str, float] = {key: 0.0 for key in CATEGORIES}

    for question in QUESTIONS:
        qid = question["id"]
        answer = answers.get(qid)
        if answer is None:
            continue
        risk = risk_value(qid, answer)
        question_risk[qid] = risk

        category = question["category"]
        category_weighted[category] += risk * question["weight"]
        category_weight_sum[category] += question["weight"]

        finding_type = question["finding_type"]
        if finding_type:
            flags[finding_type] = answer in question["risky_values"]

    category_raw = {
        key: (category_weighted[key] / category_weight_sum[key])
        if category_weight_sum[key] else 0.0
        for key in CATEGORIES
    }

    def risky(qid: str) -> float:
        """Risk value of one answer (0 when unanswered)."""
        return question_risk.get(qid, 0.0)

    # Explicitly required named numerical features
    named_features = {
        "public_phone": risky("B1"),
        "public_email": risky("B2"),
        "public_birthday": risky("B3"),
        "public_location": risky("C1"),
        "real_time_location": risky("C2"),
        "travel_plans": risky("C3"),
        "workplace_exposure": max(risky("B4"), risky("D5")),
        "school_exposure": max(risky("B5"), risky("D8")),
        "children_exposure": max(risky("D6"), risky("D7"), risky("D8")),
        "tag_review_disabled": risky("F1"),
        "mfa_disabled": risky("G1"),
        "login_alerts_disabled": risky("G2"),
        "password_reuse": risky("G3"),
        "unknown_connections": risky("E1"),
        "third_party_apps_unreviewed": risky("H1"),
        "tracker_exposure": max(risky("J7"), risky("J8")),
        "handle_reuse": risky("J4"),
        "linkage_risk": max(risky("J5"), risky("J6")),
        "historical_posts_public": max(risky("D2"), risky("J2")),
        "exif_awareness_low": risky("C7"),
        "suspicious_link_exposure": max(risky("I1"), risky("I2")),
    }

    security_controls = {
        "mfa_enabled": answers.get("G1") == "YES",
        "login_alerts_enabled": answers.get("G2") == "YES",
        "unique_passwords": answers.get("G3") == "NO",
        "sessions_reviewed": answers.get("G4") == "REGULARLY",
        "recovery_configured": answers.get("G5") == "YES",
        "password_manager": answers.get("G6") == "YES",
        "tag_review_enabled": answers.get("F1") == "YES",
        "apps_reviewed": answers.get("H1") == "REGULARLY",
        "exif_stripped": answers.get("C7") == "YES",
    }

    exposure_counts = {
        "public_answers": sum(1 for v in answers.values() if v == "PUBLIC"),
        "not_sure_answers": sum(1 for v in answers.values() if v == "NOT_SURE"),
        "risky_flags": sum(1 for v in flags.values() if v),
        "security_controls_enabled": sum(1 for v in security_controls.values() if v),
        "security_controls_total": len(security_controls),
    }

    return {
        "question_risk": question_risk,
        "category_raw": category_raw,
        "flags": flags,
        "named_features": named_features,
        "security_controls": security_controls,
        "exposure_counts": exposure_counts,
        "answered_questions": len(question_risk),
    }


# --------------------------------------------------------------------------
# 2. Category scoring (each 0-100, higher = higher assessed risk)
# --------------------------------------------------------------------------
def calculate_category_scores(features: Dict[str, Any]) -> Dict[str, float]:
    return {key: round(value * 100.0, 2) for key, value in features["category_raw"].items()}


# --------------------------------------------------------------------------
# 3. Overall weighted score
# --------------------------------------------------------------------------
def calculate_overall_score(category_scores: Dict[str, float],
                            weights: Dict[str, float] | None = None) -> float:
    active = load_weights(weights)
    total = sum(category_scores.get(key, 0.0) * active[key] for key in active)
    return round(max(0.0, min(100.0, total)), 2)


def score_breakdown(category_scores: Dict[str, float],
                    weights: Dict[str, float] | None = None) -> List[Dict[str, Any]]:
    """Explainability table: how each category contributed to the total."""
    active = load_weights(weights)
    rows = []
    for key, label in CATEGORIES.items():
        score = category_scores.get(key, 0.0)
        rows.append({
            "category": key,
            "label": label,
            "score": round(score, 2),
            "weight_percent": round(active[key] * 100, 2),
            "contribution": round(score * active[key], 2),
            "level": classify_risk_level(score),
        })
    return sorted(rows, key=lambda r: r["contribution"], reverse=True)


def explain_question_contributions(features: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Per-question explanation, sorted by risk contribution (top first)."""
    rows = []
    for qid, risk in features["question_risk"].items():
        question = QUESTION_INDEX[qid]
        rows.append({
            "question_id": qid,
            "section": question["section"],
            "category": question["category"],
            "text": question["text"],
            "risk": round(risk, 3),
            "weight": question["weight"],
            "weighted_risk": round(risk * question["weight"], 3),
        })
    return sorted(rows, key=lambda r: r["weighted_risk"], reverse=True)


__all__ = [
    "extract_privacy_features", "calculate_category_scores", "calculate_overall_score",
    "score_breakdown", "explain_question_contributions", "classify_risk_level", "DISCLAIMER",
]
