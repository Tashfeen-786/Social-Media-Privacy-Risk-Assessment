"""
improvement_simulator.py
------------------------
"What happens if I improve my settings?"

FRAMEWORK SIMULATION ONLY.
The simulated reduction shows how this educational model re-scores the same
questionnaire after selected settings changes. It does NOT guarantee
real-world safety.
"""

from typing import Any, Dict, List

from backend.services.assessment_engine import calculate_privacy_risk, validate_answers

# improvement key -> {label, changes {question_id: improved answer}}
IMPROVEMENTS: Dict[str, Dict[str, Any]] = {
    "make_phone_private": {
        "label": "Make phone number private",
        "changes": {"B1": "PRIVATE"}},
    "make_email_private": {
        "label": "Make e-mail address private",
        "changes": {"B2": "PRIVATE"}},
    "make_birthday_private": {
        "label": "Make full birth date private",
        "changes": {"B3": "PRIVATE"}},
    "make_location_private": {
        "label": "Make location / home city private",
        "changes": {"C1": "PRIVATE"}},
    "disable_realtime_location": {
        "label": "Disable real-time location sharing / live check-ins",
        "changes": {"C2": "NO", "C4": "NO", "C6": "NO"}},
    "make_travel_private": {
        "label": "Stop posting travel plans publicly",
        "changes": {"C3": "NO"}},
    "strip_photo_metadata": {
        "label": "Strip photo metadata (EXIF) before uploading",
        "changes": {"C7": "YES"}},
    "verify_unknown_requests": {
        "label": "Reject / verify unknown connection requests",
        "changes": {"E1": "NEVER", "E2": "YES"}},
    "enable_tag_review": {
        "label": "Enable tag review",
        "changes": {"F1": "YES", "F2": "NO"}},
    "enable_mfa": {
        "label": "Enable multi-factor authentication (MFA)",
        "changes": {"G1": "YES"}},
    "enable_login_alerts": {
        "label": "Enable login alerts",
        "changes": {"G2": "YES"}},
    "fix_password_reuse": {
        "label": "Stop password re-use / use a password manager",
        "changes": {"G3": "NO", "G6": "YES"}},
    "review_third_party_apps": {
        "label": "Review and revoke third-party applications",
        "changes": {"H1": "REGULARLY", "H3": "YES"}},
    "review_old_posts": {
        "label": "Review and clean up old public posts",
        "changes": {"D2": "REGULARLY", "D1": "FRIENDS"}},
    "review_privacy_settings": {
        "label": "Review platform privacy settings",
        "changes": {"J3": "REGULARLY", "A1": "FRIENDS", "A5": "NO"}},
    "improve_phishing_awareness": {
        "label": "Improve phishing / social-engineering awareness",
        "changes": {"I1": "NO", "I2": "YES", "I5": "YES"}},
    "protect_child_media": {
        "label": "Restrict media and posts involving children / minors",
        "changes": {"D6": "PRIVATE", "D7": "PRIVATE", "D8": "PRIVATE"}},
    "reduce_linkage_risk": {
        "label": "Clean up link-in-bio and linked documents",
        "changes": {"J5": "NO", "J6": "NO"}},
    "review_tracker_exposure": {
        "label": "Review trackers / privacy notice on linked sites",
        "changes": {"J7": "YES", "J8": "YES"}},
    "use_unique_handle": {
        "label": "Use different usernames / handles across platforms",
        "changes": {"J4": "NO"}},
}

# The improvement set recommended by the project specification
RECOMMENDED_SET: List[str] = [
    "make_phone_private", "make_birthday_private", "make_location_private",
    "make_travel_private", "verify_unknown_requests", "enable_tag_review",
    "enable_mfa", "enable_login_alerts", "review_third_party_apps",
]


def list_improvements() -> List[Dict[str, str]]:
    return [{"key": key, "label": value["label"]} for key, value in IMPROVEMENTS.items()]


def simulate_improvement(answers: Dict[str, str],
                         improvements: List[str],
                         weights: Dict[str, float] | None = None) -> Dict[str, Any]:
    """
    Re-score the same questionnaire with the selected improvements applied.

    Returns current score/level, applied changes, new simulated score/level,
    the assessed risk reduction and the same comparison for the exposure rubric.
    """
    cleaned = validate_answers(answers)
    unknown = [key for key in improvements if key not in IMPROVEMENTS]
    if unknown:
        raise ValueError(f"Unknown improvement(s): {', '.join(unknown)}")

    before = calculate_privacy_risk(cleaned, weights)

    simulated = dict(cleaned)
    applied: List[Dict[str, Any]] = []
    for key in improvements:
        effective = {}
        for qid, new_answer in IMPROVEMENTS[key]["changes"].items():
            if qid in simulated:
                effective[qid] = {"from": simulated[qid], "to": new_answer}
                simulated[qid] = new_answer
        applied.append({"key": key, "label": IMPROVEMENTS[key]["label"],
                        "answer_changes": effective})

    after = calculate_privacy_risk(simulated, weights)
    reduction = round(before["overall_score"] - after["overall_score"], 2)
    percent = round((reduction / before["overall_score"]) * 100, 2) if before["overall_score"] else 0.0
    rubric_reduction = round(
        before["exposure_rubric"]["score"] - after["exposure_rubric"]["score"], 2)

    category_deltas = [
        {
            "category": key,
            "label": before["category_labels"][key],
            "before": before["category_scores"][key],
            "after": after["category_scores"][key],
            "delta": round(after["category_scores"][key] - before["category_scores"][key], 2),
        }
        for key in before["category_scores"]
    ]

    return {
        "simulation_type": "FRAMEWORK SIMULATION",
        "note": ("This is a framework simulation of the educational scoring model. "
                 "It does not guarantee real-world safety."),
        "current_score": before["overall_score"],
        "current_risk_level": before["risk_level"],
        "current_category_scores": before["category_scores"],
        "current_exposure_score": before["exposure_rubric"]["score"],
        "current_exposure_level": before["exposure_rubric"]["risk_level"],
        "changes_applied": applied,
        "new_score": after["overall_score"],
        "new_risk_level": after["risk_level"],
        "new_category_scores": after["category_scores"],
        "new_exposure_score": after["exposure_rubric"]["score"],
        "new_exposure_level": after["exposure_rubric"]["risk_level"],
        "category_deltas": category_deltas,
        "risk_reduction": reduction,
        "risk_reduction_percent": percent,
        "exposure_reduction": rubric_reduction,
        "findings_before": len(before["findings"]),
        "findings_after": len(after["findings"]),
    }


__all__ = ["IMPROVEMENTS", "RECOMMENDED_SET", "list_improvements", "simulate_improvement"]
