"""
categories.py
-------------
Both scoring models used by the framework.

MODEL A - PRIVACY ASSESSMENT SCORE  (10 behaviour/configuration categories)
MODEL B - PRIVACY EXPOSURE RUBRIC   (8 exposure dimensions, PDF Step 3)

Scoring convention used everywhere:
    0   = lower assessed risk / exposure
    100 = higher assessed risk / exposure
"""

import json
import os
from typing import Dict

# ==========================================================================
# MODEL A - the 10-category privacy assessment score
# ==========================================================================
CATEGORIES: Dict[str, str] = {
    "profile_exposure": "Profile Exposure",
    "personal_information": "Personal Information",
    "location_exposure": "Location Exposure",
    "content_exposure": "Content Exposure",
    "connection_risk": "Connection Risk",
    "tagging_risk": "Tagging Risk",
    "account_security": "Account Security",
    "third_party_risk": "Third-Party App Risk",
    "social_engineering": "Social Engineering",
    "digital_footprint": "Digital Footprint",
}

# Default weighting model from the PDF (sums to 1.00)
DEFAULT_WEIGHTS: Dict[str, float] = {
    "profile_exposure": 0.10,      # Profile Visibility      10%
    "personal_information": 0.15,  # Personal Information    15%
    "location_exposure": 0.15,     # Location Privacy        15%
    "content_exposure": 0.10,      # Posts & Content         10%
    "connection_risk": 0.10,       # Connections             10%
    "tagging_risk": 0.05,          # Tagging                  5%
    "account_security": 0.15,      # Account Security        15%
    "third_party_risk": 0.05,      # Third-Party Apps         5%
    "social_engineering": 0.10,    # Social Engineering      10%
    "digital_footprint": 0.05,     # Digital Footprint        5%
}

# ==========================================================================
# MODEL B - the 8-category exposure rubric (PDF Step 3 / Step 4)
#           "Final score = min(100, sum of category contributions)"
# ==========================================================================
RUBRIC_CATEGORIES: Dict[str, str] = {
    "pii": "PII Exposure",
    "geo": "Geolocation / EXIF Leakage & Routine Trails",
    "child": "Children / Minors in Media",
    "work": "Workplace / School Disclosures",
    "privacy": "Weak Privacy Settings",
    "link": "Linkage Risks",
    "handle": "Reuse / Handle Correlation",
    "tracker": "Third-Party Trackers in Linked Sites",
}

# Maximum contribution per rubric category (sums to 100)
RUBRIC_WEIGHTS: Dict[str, int] = {
    "pii": 25,
    "geo": 20,
    "child": 15,
    "work": 10,
    "privacy": 10,
    "link": 10,
    "handle": 5,
    "tracker": 5,
}

# Risk level thresholds (higher score = higher assessed exposure)
RISK_LEVELS = [
    (0, 20, "LOW"),
    (21, 40, "MODERATE"),
    (41, 70, "HIGH"),
    (71, 100, "CRITICAL"),
]

DISCLAIMER = (
    "This is an educational privacy-risk framework. The score does NOT guarantee "
    "that an account will or will not be compromised. Weights and thresholds are "
    "educational assumptions and should be validated before being used for "
    "professional risk decisions."
)

METHODOLOGY = {
    "model_a": {
        "name": "PRIVACY ASSESSMENT SCORE",
        "description": ("Questionnaire-driven model. Ten categories score privacy and "
                        "security *behaviours and settings* from 0-100 each and are "
                        "combined with configurable weights into a 0-100 overall score."),
        "categories": len(CATEGORIES),
        "weights": DEFAULT_WEIGHTS,
    },
    "model_b": {
        "name": "PRIVACY EXPOSURE RUBRIC",
        "description": ("Exposure-dimension model from the project rubric. Eight "
                        "dimensions each contribute capped points; the final score is "
                        "min(100, sum of contributions)."),
        "categories": len(RUBRIC_CATEGORIES),
        "max_points": RUBRIC_WEIGHTS,
    },
    "relationship": ("The two models are COMPLEMENTARY, not equivalent. Model A measures "
                     "behaviour and configuration quality; Model B measures specific "
                     "exposure dimensions such as PII, geolocation/EXIF, children in "
                     "media, linkage and trackers. They use different mathematics "
                     "(weighted mean vs capped additive points) and will normally "
                     "produce different numbers for the same person. Neither model "
                     "guarantees real-world safety or compromise; both are educational."),
}


def classify_risk_level(score: float) -> str:
    """Map a 0-100 score to LOW / MODERATE / HIGH / CRITICAL."""
    value = max(0.0, min(100.0, float(score)))
    if value <= 20:
        return "LOW"
    if value <= 40:
        return "MODERATE"
    if value <= 70:
        return "HIGH"
    return "CRITICAL"


def load_weights(custom: Dict[str, float] | None = None) -> Dict[str, float]:
    """
    Return the active Model-A weighting.

    Priority:  explicit argument  >  PRIVACY_WEIGHTS_FILE env var  >  defaults.
    Weights are normalised to sum to 1.0, so a partial override can never
    silently break the default configuration.
    """
    weights = dict(DEFAULT_WEIGHTS)

    weights_file = os.getenv("PRIVACY_WEIGHTS_FILE", "").strip()
    if weights_file and os.path.exists(weights_file):
        try:
            with open(weights_file, "r", encoding="utf-8") as handle:
                file_weights = json.load(handle)
            for key, value in file_weights.items():
                if key in weights:
                    weights[key] = float(value)
        except (ValueError, OSError):
            weights = dict(DEFAULT_WEIGHTS)  # fail safe -> defaults

    if custom:
        for key, value in custom.items():
            if key in weights and value is not None:
                weights[key] = max(0.0, float(value))

    total = sum(weights.values())
    if total <= 0:
        return dict(DEFAULT_WEIGHTS)
    return {key: value / total for key, value in weights.items()}


def load_rubric_weights(custom: Dict[str, int] | None = None) -> Dict[str, int]:
    """Return the active Model-B category caps (configurable, never negative)."""
    caps = dict(RUBRIC_WEIGHTS)
    if custom:
        for key, value in custom.items():
            if key in caps and value is not None:
                caps[key] = max(0, int(value))
    return caps
