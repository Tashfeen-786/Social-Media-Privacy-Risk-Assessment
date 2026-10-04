"""
recommendation_engine.py
------------------------
Generates personalised, prioritised privacy recommendations from findings.

Priority model:
    IMMEDIATE      -> act now, highest assessed exposure reduction
    IMPORTANT      -> act soon
    GOOD PRACTICE  -> ongoing hygiene

Coverage required by the specification (all implemented through the finding
catalogue): profile privacy, personal information, location, workplace/school,
children/minors, tagging, connections, MFA, login alerts, third-party apps,
tracker awareness, old posts, suspicious links, photo metadata, digital
footprint, linkage risks and handle reuse.
"""

from typing import Any, Dict, List

from backend.models.categories import CATEGORIES
from backend.services.findings_engine import FINDING_CATALOG

PRIORITY_ORDER = {"IMMEDIATE": 0, "IMPORTANT": 1, "GOOD PRACTICE": 2}

# Always-useful hygiene recommendations appended after the personalised ones.
BASELINE_RECOMMENDATIONS = [
    {"finding_type": "baseline_review", "category": "digital_footprint",
     "recommendation": "Repeat this privacy assessment every 3-6 months and after any "
                       "platform settings change.",
     "priority": "GOOD PRACTICE"},
    {"finding_type": "baseline_checklist", "category": "profile_exposure",
     "recommendation": "Download the Social Media Privacy Checklist and work through it "
                       "one platform at a time.",
     "priority": "GOOD PRACTICE"},
    {"finding_type": "baseline_metadata", "category": "location_exposure",
     "recommendation": "Use the local photo metadata viewer before posting images to "
                       "confirm no EXIF location or device data is attached.",
     "priority": "GOOD PRACTICE"},
]


def generate_recommendations(findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Map findings to prioritised recommendations (deterministic order)."""
    recommendations: List[Dict[str, Any]] = []
    seen = set()

    for finding in findings:
        ftype = finding["finding_type"]
        if ftype in seen:
            continue
        seen.add(ftype)
        meta = FINDING_CATALOG[ftype]
        recommendations.append({
            "finding_type": ftype,
            "category": meta["category"],
            "category_label": CATEGORIES[meta["category"]],
            "trigger": meta["finding"],
            "recommendation": meta["action"],
            "priority": meta["priority"],
            "severity": meta["severity"],
        })

    for baseline in BASELINE_RECOMMENDATIONS:
        recommendations.append({
            "finding_type": baseline["finding_type"],
            "category": baseline["category"],
            "category_label": CATEGORIES[baseline["category"]],
            "trigger": "General privacy hygiene",
            "recommendation": baseline["recommendation"],
            "priority": baseline["priority"],
            "severity": "LOW",
        })

    recommendations.sort(key=lambda r: (PRIORITY_ORDER[r["priority"]], r["trigger"]))
    return recommendations


def priority_summary(recommendations: List[Dict[str, Any]]) -> Dict[str, int]:
    summary = {"IMMEDIATE": 0, "IMPORTANT": 0, "GOOD PRACTICE": 0}
    for rec in recommendations:
        summary[rec["priority"]] += 1
    return summary


__all__ = ["generate_recommendations", "priority_summary", "PRIORITY_ORDER"]
