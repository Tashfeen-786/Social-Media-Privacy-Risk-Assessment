"""
exposure_rubric.py
------------------
MODEL B - the 8-category PRIVACY EXPOSURE RUBRIC.

Two entry points, both producing the same rubric shape:

  1. calculate_exposure_rubric(answers)
         questionnaire-driven: maps each answer's risk value onto the rubric
         points declared in backend/models/questions.py.

  2. score_profile(profile, posts)
         file-driven rule engine over the project's profile.json / posts.json
         data contract (regex + keyword rules, exactly as specified in the
         project rubric): PII, GEO/EXIF/routine, CHILD, WORK, PRIVACY, LINK,
         HANDLE, TRACKER.

Category caps (configurable):
    PII 25 | GEO 20 | CHILD 15 | WORK 10 | PRIVACY 10 | LINK 10 |
    HANDLE 5 | TRACKER 5                       ->  final = min(100, sum)

ETHICS: the rule engine only ever reads SYNTHETIC / self-owned exported files
supplied voluntarily. It performs no scraping, no network calls, no account
enumeration and no lookup of real people.
"""

import re
from typing import Any, Dict, List

from backend.models.categories import (
    RUBRIC_CATEGORIES,
    classify_risk_level,
    load_rubric_weights,
)
from backend.models.questions import QUESTIONS, risk_value

# --------------------------------------------------------------------------
# Rule-engine vocabulary (from the project rubric)
# --------------------------------------------------------------------------
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(\+?\d[\s-]?){9,}")

WORKWORDS = {"badge", "id card", "hq", "office", "3rd floor", "floor", "desk",
             "shift", "campus", "staff room", "room no", "cubicle"}
CHILD_HINTS = {"my kid", "my child", "daughter", "son", "#kids", "#school",
               "kindergarten", "playschool", "school drop"}
ROUTINE_HINTS = {"every day", "daily", "7am run", "commute", "school drop",
                 "every morning", "usual spot", "same time"}
AGGREGATOR_HINTS = ("linktr.ee", "pastebin", "linkin.bio", "bio.link")
TRACKER_HINTS = ("google-analytics", "gtag", "facebook.net", "hotjar",
                 "doubleclick", "mixpanel")


def _empty_points() -> Dict[str, float]:
    return {key: 0.0 for key in RUBRIC_CATEGORIES}


def _assemble(points: Dict[str, float], findings: List[Dict[str, Any]],
              caps: Dict[str, int], source: str) -> Dict[str, Any]:
    """Cap each category, sum, clamp to 100 and build the response object."""
    capped = {key: round(min(points.get(key, 0.0), caps[key]), 2)
              for key in RUBRIC_CATEGORIES}
    total = round(min(100.0, sum(capped.values())), 2)
    return {
        "model": "B",
        "name": "PRIVACY EXPOSURE RUBRIC",
        "source": source,
        "score": total,
        "risk_level": classify_risk_level(total),
        "categories": [
            {
                "key": key,
                "label": RUBRIC_CATEGORIES[key],
                "points": capped[key],
                "max_points": caps[key],
                "raw_points": round(points.get(key, 0.0), 2),
                "capped": points.get(key, 0.0) > caps[key],
                "percent_of_cap": round((capped[key] / caps[key] * 100), 1) if caps[key] else 0.0,
            }
            for key in RUBRIC_CATEGORIES
        ],
        "category_points": capped,
        "caps": caps,
        "findings": findings,
        "formula": "final_score = min(100, sum(min(category_points, category_cap)))",
        "note": ("Complementary to the 10-category PRIVACY ASSESSMENT SCORE; the two "
                 "models are not mathematically equivalent. Educational model only."),
    }


# ==========================================================================
# 1. Questionnaire-driven rubric
# ==========================================================================
def calculate_exposure_rubric(answers: Dict[str, str],
                              caps: Dict[str, int] | None = None) -> Dict[str, Any]:
    """Compute the 8-category rubric from validated questionnaire answers."""
    active_caps = load_rubric_weights(caps)
    points = _empty_points()
    findings: List[Dict[str, Any]] = []

    for question in QUESTIONS:
        mapping = question.get("rubric") or {}
        if not mapping:
            continue
        answer = answers.get(question["id"])
        if answer is None:
            continue
        risk = risk_value(question["id"], answer)
        if risk <= 0:
            continue
        for rubric_key, max_points in mapping.items():
            contribution = risk * max_points
            points[rubric_key] += contribution
            if risk >= 0.5:
                findings.append({
                    "cat": rubric_key.upper(),
                    "category_label": RUBRIC_CATEGORIES[rubric_key],
                    "item": question["text"],
                    "question_id": question["id"],
                    "answer": answer,
                    "points": round(contribution, 2),
                })

    findings.sort(key=lambda f: f["points"], reverse=True)
    return _assemble(points, findings, active_caps, "questionnaire")


# ==========================================================================
# 2. File-driven rule engine over the profile.json / posts.json contract
# ==========================================================================
def score_profile(profile: Dict[str, Any], posts: List[Dict[str, Any]],
                  caps: Dict[str, int] | None = None) -> Dict[str, Any]:
    """
    Rule-based analyser for a SYNTHETIC exported profile + posts payload.

    Returns the rubric object (score, capped category points, findings with a
    human-readable reason and a specific fix for every item).
    """
    active_caps = load_rubric_weights(caps)
    points = _empty_points()
    findings: List[Dict[str, Any]] = []
    posts = posts or []

    def add(cat: str, value: float, item: str, fix: str):
        points[cat] += value
        findings.append({
            "cat": cat.upper(),
            "category_label": RUBRIC_CATEGORIES[cat],
            "item": item,
            "fix": fix,
            "points": value,
        })

    # ---------------- PII exposure (max 25) ------------------------------
    text_fields = " ".join([
        str(profile.get("bio", "") or ""),
        str(profile.get("email", "") or ""),
        str(profile.get("phone", "") or ""),
    ])
    if EMAIL_RE.search(text_fields):
        add("pii", 10, "E-mail address visible in bio/profile",
            "Remove the e-mail address; use a contact form or a masked address.")
    if PHONE_RE.search(text_fields):
        add("pii", 10, "Phone number publicly visible",
            "Remove the phone number; switch to business contact options.")
    if profile.get("location"):
        add("pii", 5, "Home city visible on the profile",
            "Remove precise location; keep region-level information only.")
    if profile.get("birthday") or profile.get("dob"):
        add("pii", 5, "Birth date present in the exported profile",
            "Hide the full birth date; show only day/month or nothing.")

    # ---------------- Geolocation / EXIF / routine (max 20) --------------
    for post in posts:
        pid = post.get("id", "?")
        media = post.get("media", {}) or {}
        exif = media.get("exif", {}) or {}
        if post.get("geo"):
            add("geo", 4, f"Geotagged post {pid}",
                "Disable geotagging; remove past geo data from sensitive posts.")
        if exif.get("created_local") or exif.get("DateTimeOriginal"):
            add("geo", 2, f"EXIF timestamp leak in {pid}",
                "Strip EXIF metadata before uploading.")
        if exif.get("gps") or exif.get("GPSInfo"):
            add("geo", 4, f"EXIF GPS coordinates embedded in {pid}",
                "Strip EXIF metadata; disable camera location tagging.")
        text = (post.get("text") or "").lower()
        if any(hint in text for hint in ROUTINE_HINTS):
            add("geo", 2, f"Routine disclosed in {pid}",
                "Avoid recurring time/place patterns in posts.")

    # ---------------- Children / minors (max 15) -------------------------
    for post in posts:
        pid = post.get("id", "?")
        media = post.get("media", {}) or {}
        if media.get("is_child_present"):
            add("child", 8, f"Child appears in post {pid} (public account)",
                "Make the account private, or remove / blur children's faces.")
        text = (post.get("text") or "").lower()
        if any(hint in text for hint in CHILD_HINTS):
            add("child", 2, f"Child-related caption in {pid}",
                "Avoid naming schools, routines or activities of minors publicly.")

    # ---------------- Workplace / school (max 10) ------------------------
    for post in posts:
        text = (post.get("text") or "").lower()
        if any(word in text for word in WORKWORDS):
            add("work", 5, f"Workplace / school detail in {post.get('id', '?')}",
                "Avoid badge, room or entry details; post generic work updates.")

    # ---------------- Weak privacy settings (max 10) ---------------------
    privacy = profile.get("privacy", {}) or {}
    if not privacy.get("account_private", False):
        add("privacy", 6, "Account is public",
            "Set the account to private, or limit the story/post audience.")
    if privacy.get("show_activity", False):
        add("privacy", 2, "Activity status visible",
            "Turn off activity / last-seen indicators.")
    if privacy.get("allow_message_requests", True):
        add("privacy", 2, "Open message requests",
            "Restrict who can message you to connections only.")

    # ---------------- Linkage risks (max 10) -----------------------------
    for url in profile.get("links", []) or []:
        lowered = str(url).lower()
        if any(hint in lowered for hint in AGGREGATOR_HINTS):
            add("link", 5, f"Link aggregator in bio: {url}",
                "Ensure linked documents hide e-mail/phone; remove public spreadsheets.")
        if "github.com" in lowered:
            add("link", 3, "Code repository linked from the profile",
                "Scan repositories for .env files, keys and PII; add a SECURITY.md.")
        if lowered.endswith((".pdf", ".doc", ".docx", ".xls", ".xlsx", ".csv")):
            add("link", 3, f"Public document linked: {url}",
                "Review the document for contact details before sharing publicly.")

    # ---------------- Handle reuse / correlation (max 5) -----------------
    username = (profile.get("username") or "").strip().lower()
    if username:
        reused = [u for u in (profile.get("links", []) or []) if username in str(u).lower()]
        if reused:
            add("handle", 3, "Same handle re-used across multiple sites",
                "Consider unique handles, or privacy mode on secondary accounts.")
        if profile.get("handle_reused_elsewhere"):
            add("handle", 2, "Handle self-reported as re-used on other platforms",
                "Use different handles for personal and public-facing accounts.")

    # ---------------- Third-party trackers (max 5) -----------------------
    website = str(profile.get("website") or "")
    site_meta = profile.get("site_meta", {}) or {}
    if website:
        add("tracker", 3, "Personal site linked; it may include third-party trackers",
            "Add a cookie/privacy notice and reduce third-party scripts.")
    declared = [t for t in (site_meta.get("third_party_scripts") or [])
                if any(hint in str(t).lower() for hint in TRACKER_HINTS)]
    if declared:
        add("tracker", 2, f"Tracker scripts reported on the linked site: "
                          f"{', '.join(declared[:3])}",
            "Remove or gate analytics/advertising scripts behind consent.")

    findings.sort(key=lambda f: f["points"], reverse=True)
    result = _assemble(points, findings, active_caps, "profile_posts_files")
    result["tracker_disclaimer"] = (
        "The tracker check is a basic educational check based only on information "
        "declared in the supplied synthetic file. It is NOT a complete browser-level "
        "tracker audit, and no website is crawled or contacted.")
    return result


__all__ = ["calculate_exposure_rubric", "score_profile", "RUBRIC_CATEGORIES"]
