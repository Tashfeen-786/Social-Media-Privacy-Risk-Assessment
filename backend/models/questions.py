"""
questions.py
------------
Canonical definition of the Social Media Privacy Risk Assessment questionnaire.

The questionnaire is organised into the PDF's ten sections (CATEGORY A .. J) and
covers all 20 privacy areas required by the project specification:

     1 Profile visibility            11 Third-party application access
     2 Personal-information exposure 12 Account authentication
     3 Contact-information exposure  13 MFA usage
     4 Location exposure             14 Password reuse awareness
     5 Workplace/education exposure  15 Login alerts
     6 Birthday exposure             16 Unknown connection requests
     7 Family/relationship info      17 Suspicious links/messages
     8 Post visibility               18 Photo metadata awareness
     9 Friend/follower controls      19 Historical posts
    10 Tagging permissions           20 Social-engineering exposure

PRIVACY NOTE (Privacy by Design / Data Minimisation):
    No question asks for an actual phone number, e-mail address, postal address,
    birth date, password, child's name/school or message content.  Sensitive
    attributes are probed only as *visibility* questions, e.g.
    "Is your phone number publicly visible?" -> PUBLIC / FRIENDS / PRIVATE.

Each question carries machine readable metadata so the whole score stays
deterministic and explainable:

    id            unique question id (A1, B3, ...)
    section       questionnaire section (CATEGORY A .. J)
    category      one of the ten scoring categories (model A)
    text          question wording shown in the UI
    type          answer widget type (visibility | yesno | frequency)
    options       list of {value, label, risk} - risk in [0.0 .. 1.0]
    weight        relative weight of the question *inside* its category
    finding_type  machine key linking a risky answer to a finding
    risky_values  answer values that trigger the finding
    rubric        optional {rubric_category: max_points} contribution used by
                  the PDF's 8-category exposure rubric (model B)
"""

from typing import Any, Dict, List

# --------------------------------------------------------------------------
# Re-usable answer option sets
# --------------------------------------------------------------------------

VISIBILITY = [
    {"value": "PUBLIC", "label": "Public", "risk": 1.0},
    {"value": "FRIENDS", "label": "Friends / Followers only", "risk": 0.4},
    {"value": "PRIVATE", "label": "Private / Only me", "risk": 0.0},
    {"value": "NOT_SURE", "label": "Not sure", "risk": 0.7},
]

# "YES" is the risky answer
YESNO_RISKY = [
    {"value": "YES", "label": "Yes", "risk": 1.0},
    {"value": "SOMETIMES", "label": "Sometimes", "risk": 0.5},
    {"value": "NO", "label": "No", "risk": 0.0},
    {"value": "NOT_SURE", "label": "Not sure", "risk": 0.7},
]

# "YES" is the safe answer (a protective control is enabled)
YESNO_SAFE = [
    {"value": "YES", "label": "Yes", "risk": 0.0},
    {"value": "SOMETIMES", "label": "Sometimes", "risk": 0.5},
    {"value": "NO", "label": "No", "risk": 1.0},
    {"value": "NOT_SURE", "label": "Not sure", "risk": 0.8},
]

FREQ_REVIEW = [  # how often a protective review happens
    {"value": "REGULARLY", "label": "Regularly", "risk": 0.0},
    {"value": "RARELY", "label": "Rarely", "risk": 0.6},
    {"value": "NEVER", "label": "Never", "risk": 1.0},
    {"value": "NOT_SURE", "label": "Not sure", "risk": 0.8},
]

FREQ_ACCEPT = [  # how often a risky behaviour happens
    {"value": "NEVER", "label": "Never", "risk": 0.0},
    {"value": "RARELY", "label": "Rarely", "risk": 0.35},
    {"value": "SOMETIMES", "label": "Sometimes", "risk": 0.7},
    {"value": "OFTEN", "label": "Often", "risk": 1.0},
]


def _q(qid, section, category, text, qtype, options, weight=1.0,
       finding_type=None, risky_values=None, rubric=None, area=None) -> Dict[str, Any]:
    return {
        "id": qid,
        "section": section,
        "category": category,
        "text": text,
        "type": qtype,
        "options": options,
        "weight": weight,
        "finding_type": finding_type,
        "risky_values": risky_values or [],
        "rubric": rubric or {},
        "area": area or "",
    }


SECTION_A = "CATEGORY A: Profile Visibility"
SECTION_B = "CATEGORY B: Personal Information"
SECTION_C = "CATEGORY C: Location Privacy"
SECTION_D = "CATEGORY D: Posts & Content"
SECTION_E = "CATEGORY E: Friends / Followers"
SECTION_F = "CATEGORY F: Tagging & Mentions"
SECTION_G = "CATEGORY G: Authentication & Account Security"
SECTION_H = "CATEGORY H: Third-Party Apps"
SECTION_I = "CATEGORY I: Messaging & Social Engineering"
SECTION_J = "CATEGORY J: Digital Footprint"

QUESTIONS: List[Dict[str, Any]] = [
    # ================= CATEGORY A: Profile Visibility =====================
    _q("A1", SECTION_A, "profile_exposure",
       "Is your main social-media profile visible to the public?",
       "visibility", VISIBILITY, 1.4, "public_profile", ["PUBLIC", "NOT_SURE"],
       {"privacy": 5}, "1 Profile visibility"),
    _q("A2", SECTION_A, "profile_exposure",
       "Is your profile photo visible to everyone (not just connections)?",
       "visibility", VISIBILITY, 1.0, "public_profile_photo", ["PUBLIC", "NOT_SURE"],
       None, "1 Profile visibility"),
    _q("A3", SECTION_A, "profile_exposure",
       "Is your friends / followers list visible to the public?",
       "visibility", VISIBILITY, 1.0, "public_friend_list", ["PUBLIC", "NOT_SURE"],
       {"privacy": 2}, "9 Friend/follower controls"),
    _q("A4", SECTION_A, "profile_exposure",
       "Can anyone on the internet find your profile through a search engine?",
       "yesno", YESNO_RISKY, 1.0, "search_engine_indexed", ["YES", "NOT_SURE"],
       {"privacy": 2}, "1 Profile visibility"),
    _q("A5", SECTION_A, "profile_exposure",
       "Is your activity status / last-seen indicator visible to others?",
       "yesno", YESNO_RISKY, 0.8, "activity_status_visible", ["YES", "NOT_SURE"],
       {"privacy": 2}, "1 Profile visibility"),

    # ================= CATEGORY B: Personal Information ===================
    _q("B1", SECTION_B, "personal_information",
       "Is your phone number publicly visible on your profile? "
       "(Do NOT enter the number itself.)",
       "visibility", VISIBILITY, 1.5, "public_phone", ["PUBLIC", "NOT_SURE"],
       {"pii": 10}, "3 Contact-information exposure"),
    _q("B2", SECTION_B, "personal_information",
       "Is your personal e-mail address publicly visible? "
       "(Do NOT enter the address itself.)",
       "visibility", VISIBILITY, 1.3, "public_email", ["PUBLIC", "NOT_SURE"],
       {"pii": 8}, "3 Contact-information exposure"),
    _q("B3", SECTION_B, "personal_information",
       "Is your full birth date (day, month and year) publicly visible?",
       "visibility", VISIBILITY, 1.3, "public_birthday", ["PUBLIC", "NOT_SURE"],
       {"pii": 5}, "6 Birthday exposure"),
    _q("B4", SECTION_B, "personal_information",
       "Is your current workplace / employer publicly visible?",
       "visibility", VISIBILITY, 1.0, "public_workplace", ["PUBLIC"],
       {"work": 4}, "5 Workplace/education exposure"),
    _q("B5", SECTION_B, "personal_information",
       "Is your school / college / university publicly visible?",
       "visibility", VISIBILITY, 0.9, "public_education", ["PUBLIC"],
       {"work": 3}, "5 Workplace/education exposure"),
    _q("B6", SECTION_B, "personal_information",
       "Are names of close family members or relationship details publicly visible?",
       "visibility", VISIBILITY, 0.9, "public_family", ["PUBLIC"],
       None, "7 Family/relationship information"),

    # ================= CATEGORY C: Location Privacy =======================
    _q("C1", SECTION_C, "location_exposure",
       "Is your home city / current location publicly visible?",
       "visibility", VISIBILITY, 1.2, "public_location", ["PUBLIC", "NOT_SURE"],
       {"pii": 5}, "4 Location exposure"),
    _q("C2", SECTION_C, "location_exposure",
       "Do you post real-time check-ins while you are still at that place?",
       "yesno", YESNO_RISKY, 1.5, "realtime_location", ["YES", "SOMETIMES", "NOT_SURE"],
       {"geo": 6}, "4 Location exposure"),
    _q("C3", SECTION_C, "location_exposure",
       "Do you publicly announce travel plans or vacations before/during the trip?",
       "yesno", YESNO_RISKY, 1.3, "travel_plans", ["YES", "SOMETIMES"],
       {"geo": 5}, "4 Location exposure"),
    _q("C4", SECTION_C, "location_exposure",
       "Do your photos get posted with automatic location tags (geotagging) enabled?",
       "yesno", YESNO_RISKY, 1.1, "photo_geotags", ["YES", "SOMETIMES", "NOT_SURE"],
       {"geo": 5}, "4 Location exposure"),
    _q("C5", SECTION_C, "location_exposure",
       "Have you shared photos that clearly show your home, street or house number?",
       "yesno", YESNO_RISKY, 1.0, "home_visible_photos", ["YES", "SOMETIMES"],
       {"pii": 5}, "4 Location exposure"),
    _q("C6", SECTION_C, "location_exposure",
       "Is 'live location' sharing enabled with people outside your close circle?",
       "yesno", YESNO_RISKY, 1.0, "live_location_sharing", ["YES", "SOMETIMES", "NOT_SURE"],
       {"geo": 4}, "4 Location exposure"),
    _q("C7", SECTION_C, "location_exposure",
       "Do you remove photo metadata (EXIF: camera, timestamp, GPS) before uploading?",
       "yesno", YESNO_SAFE, 1.1, "exif_not_stripped", ["NO", "NOT_SURE"],
       {"geo": 4}, "18 Photo metadata awareness"),

    # ================= CATEGORY D: Posts & Content ========================
    _q("D1", SECTION_D, "content_exposure",
       "Are your posts visible to the public by default?",
       "visibility", VISIBILITY, 1.3, "public_posts", ["PUBLIC", "NOT_SURE"],
       None, "8 Post visibility"),
    _q("D2", SECTION_D, "content_exposure",
       "Have you reviewed and cleaned up your old public posts in the last year?",
       "frequency", FREQ_REVIEW, 1.2, "old_posts_not_reviewed", ["NEVER", "RARELY", "NOT_SURE"],
       None, "19 Historical posts"),
    _q("D3", SECTION_D, "content_exposure",
       "Do you post photos of documents, tickets, IDs or boarding passes?",
       "yesno", YESNO_RISKY, 1.1, "document_photos", ["YES", "SOMETIMES"],
       None, "8 Post visibility"),
    _q("D4", SECTION_D, "content_exposure",
       "Do your posts reveal a daily routine (gym, office, commute, school run timings)?",
       "yesno", YESNO_RISKY, 0.9, "routine_exposure", ["YES", "SOMETIMES"],
       {"geo": 3}, "4 Location exposure"),
    _q("D5", SECTION_D, "content_exposure",
       "Have you posted photos showing work/school badges, ID cards, desks, "
       "room or floor numbers?",
       "yesno", YESNO_RISKY, 1.0, "workplace_media", ["YES", "SOMETIMES"],
       {"work": 6}, "5 Workplace/education exposure"),
    _q("D6", SECTION_D, "content_exposure",
       "Are photos or videos that include children / minors publicly visible?",
       "visibility", VISIBILITY, 1.2, "child_media_public", ["PUBLIC", "NOT_SURE"],
       {"child": 6}, "8 Post visibility"),
    _q("D7", SECTION_D, "content_exposure",
       "Are posts that mention children / minors (activities, milestones) publicly visible?",
       "visibility", VISIBILITY, 1.0, "child_posts_public", ["PUBLIC", "NOT_SURE"],
       {"child": 6}, "8 Post visibility"),
    _q("D8", SECTION_D, "content_exposure",
       "Is school-related information involving minors (school name, timings, routes) "
       "publicly visible?",
       "visibility", VISIBILITY, 1.1, "child_school_public", ["PUBLIC", "NOT_SURE"],
       {"child": 6}, "5 Workplace/education exposure"),

    # ================= CATEGORY E: Friends / Followers ====================
    _q("E1", SECTION_E, "connection_risk",
       "How often do you accept connection requests from people you do not know?",
       "frequency", FREQ_ACCEPT, 1.5, "unknown_connections", ["OFTEN", "SOMETIMES"],
       None, "16 Unknown connection requests"),
    _q("E2", SECTION_E, "connection_risk",
       "Do you verify unfamiliar profiles (mutual friends, account age) before accepting?",
       "yesno", YESNO_SAFE, 1.2, "no_request_verification", ["NO", "NOT_SURE"],
       None, "16 Unknown connection requests"),
    _q("E3", SECTION_E, "connection_risk",
       "Have you reviewed and removed inactive or unknown connections recently?",
       "frequency", FREQ_REVIEW, 1.0, "connections_not_reviewed", ["NEVER", "RARELY"],
       None, "9 Friend/follower controls"),
    _q("E4", SECTION_E, "connection_risk",
       "Can people who are not connected to you send you direct messages?",
       "yesno", YESNO_RISKY, 0.9, "open_dm", ["YES", "NOT_SURE"],
       {"privacy": 2}, "9 Friend/follower controls"),
    _q("E5", SECTION_E, "connection_risk",
       "Have you ever noticed a duplicate / impersonating account using your photos?",
       "yesno", YESNO_RISKY, 0.8, "impersonation_seen", ["YES"],
       None, "20 Social-engineering exposure"),

    # ================= CATEGORY F: Tagging & Mentions =====================
    _q("F1", SECTION_F, "tagging_risk",
       "Is tag review (approve tags before they appear) enabled?",
       "yesno", YESNO_SAFE, 1.5, "tag_review_disabled", ["NO", "NOT_SURE"],
       None, "10 Tagging permissions"),
    _q("F2", SECTION_F, "tagging_risk",
       "Can anyone tag you in posts or photos?",
       "yesno", YESNO_RISKY, 1.2, "open_tagging", ["YES", "NOT_SURE"],
       None, "10 Tagging permissions"),
    _q("F3", SECTION_F, "tagging_risk",
       "Are posts you are tagged in visible to the public?",
       "visibility", VISIBILITY, 1.0, "public_tagged_posts", ["PUBLIC", "NOT_SURE"],
       None, "10 Tagging permissions"),
    _q("F4", SECTION_F, "tagging_risk",
       "Can unknown accounts mention your profile in their posts?",
       "yesno", YESNO_RISKY, 0.9, "open_mentions", ["YES", "NOT_SURE"],
       None, "10 Tagging permissions"),

    # ========== CATEGORY G: Authentication & Account Security =============
    _q("G1", SECTION_G, "account_security",
       "Is multi-factor authentication (MFA / 2FA) enabled on your account?",
       "yesno", YESNO_SAFE, 2.0, "mfa_disabled", ["NO", "NOT_SURE"],
       None, "13 MFA usage"),
    _q("G2", SECTION_G, "account_security",
       "Are login alerts / unrecognised-login notifications enabled?",
       "yesno", YESNO_SAFE, 1.3, "login_alerts_disabled", ["NO", "NOT_SURE"],
       None, "15 Login alerts"),
    _q("G3", SECTION_G, "account_security",
       "Do you re-use the same password on more than one website? "
       "(Do NOT type any password.)",
       "yesno", YESNO_RISKY, 1.6, "password_reuse", ["YES", "SOMETIMES", "NOT_SURE"],
       None, "14 Password reuse awareness"),
    _q("G4", SECTION_G, "account_security",
       "Do you review active login sessions / connected devices?",
       "frequency", FREQ_REVIEW, 1.0, "sessions_not_reviewed", ["NEVER", "RARELY"],
       None, "12 Account authentication"),
    _q("G5", SECTION_G, "account_security",
       "Have you reviewed your account recovery options (backup codes / recovery e-mail)?",
       "yesno", YESNO_SAFE, 0.9, "no_recovery_setup", ["NO", "NOT_SURE"],
       None, "12 Account authentication"),
    _q("G6", SECTION_G, "account_security",
       "Do you use a password manager or otherwise unique strong passwords?",
       "yesno", YESNO_SAFE, 1.0, "no_password_manager", ["NO", "NOT_SURE"],
       None, "14 Password reuse awareness"),

    # ================= CATEGORY H: Third-Party Apps =======================
    _q("H1", SECTION_H, "third_party_risk",
       "How often do you review the third-party apps connected to your account?",
       "frequency", FREQ_REVIEW, 1.5, "apps_not_reviewed", ["NEVER", "RARELY", "NOT_SURE"],
       None, "11 Third-party application access"),
    _q("H2", SECTION_H, "third_party_risk",
       "Do you log in to other websites using your social-media account "
       "('Sign in with…')?",
       "yesno", YESNO_RISKY, 1.0, "social_login_used", ["YES", "SOMETIMES"],
       None, "11 Third-party application access"),
    _q("H3", SECTION_H, "third_party_risk",
       "Have you removed apps / quizzes / games and old integrations you no longer use?",
       "yesno", YESNO_SAFE, 1.1, "unused_apps_present", ["NO", "NOT_SURE"],
       None, "11 Third-party application access"),
    _q("H4", SECTION_H, "third_party_risk",
       "Do you check what permissions an app requests before authorising it?",
       "yesno", YESNO_SAFE, 1.0, "permissions_not_checked", ["NO", "NOT_SURE"],
       None, "11 Third-party application access"),

    # ========== CATEGORY I: Messaging & Social Engineering ================
    _q("I1", SECTION_I, "social_engineering",
       "Do you click links received in unexpected messages from unknown senders?",
       "yesno", YESNO_RISKY, 1.5, "suspicious_links", ["YES", "SOMETIMES", "NOT_SURE"],
       None, "17 Suspicious links/messages"),
    _q("I2", SECTION_I, "social_engineering",
       "Are you confident you can recognise a phishing / fake-support message?",
       "yesno", YESNO_SAFE, 1.2, "low_phishing_awareness", ["NO", "NOT_SURE"],
       None, "17 Suspicious links/messages"),
    _q("I3", SECTION_I, "social_engineering",
       "Have you ever shared a one-time verification code (OTP) with someone?",
       "yesno", YESNO_RISKY, 1.5, "otp_shared", ["YES", "SOMETIMES"],
       None, "20 Social-engineering exposure"),
    _q("I4", SECTION_I, "social_engineering",
       "Do you share personal details or respond to giveaway / prize messages in DMs?",
       "yesno", YESNO_RISKY, 1.1, "scam_engagement", ["YES", "SOMETIMES"],
       None, "20 Social-engineering exposure"),
    _q("I5", SECTION_I, "social_engineering",
       "Do you verify unusual requests from 'known' contacts through another channel?",
       "yesno", YESNO_SAFE, 1.0, "no_out_of_band_verification", ["NO", "NOT_SURE"],
       None, "20 Social-engineering exposure"),

    # ================= CATEGORY J: Digital Footprint ======================
    _q("J1", SECTION_J, "digital_footprint",
       "Have you searched your own name to see what is publicly visible about you?",
       "yesno", YESNO_SAFE, 1.2, "footprint_unknown", ["NO", "NOT_SURE"],
       None, "19 Historical posts"),
    _q("J2", SECTION_J, "digital_footprint",
       "Do you still keep old / unused social-media accounts that are public?",
       "yesno", YESNO_RISKY, 1.2, "abandoned_accounts", ["YES", "NOT_SURE"],
       None, "19 Historical posts"),
    _q("J3", SECTION_J, "digital_footprint",
       "How often do you review your platform privacy settings?",
       "frequency", FREQ_REVIEW, 1.4, "privacy_settings_not_reviewed",
       ["NEVER", "RARELY", "NOT_SURE"], None, "1 Profile visibility"),
    _q("J4", SECTION_J, "digital_footprint",
       "Do you use the same username / handle across many public platforms?",
       "yesno", YESNO_RISKY, 0.9, "handle_reuse", ["YES", "NOT_SURE"],
       {"handle": 5}, "19 Historical posts"),
    _q("J5", SECTION_J, "digital_footprint",
       "Do you use a public link-in-bio aggregator page that lists your other profiles?",
       "yesno", YESNO_RISKY, 0.9, "link_aggregator", ["YES", "NOT_SURE"],
       {"link": 5}, "19 Historical posts"),
    _q("J6", SECTION_J, "digital_footprint",
       "Could the pages, documents or repositories you link to contain personal "
       "contact details?",
       "yesno", YESNO_RISKY, 1.0, "linked_docs_pii", ["YES", "NOT_SURE"],
       {"link": 5}, "2 Personal-information exposure"),
    _q("J7", SECTION_J, "digital_footprint",
       "Do you know whether the websites linked from your profile use third-party "
       "trackers or analytics?",
       "yesno", YESNO_SAFE, 0.8, "tracker_awareness_low", ["NO", "NOT_SURE"],
       {"tracker": 3}, "19 Historical posts"),
    _q("J8", SECTION_J, "digital_footprint",
       "Does your personal site / blog (if any) publish a privacy or cookie notice?",
       "yesno", YESNO_SAFE, 0.7, "no_privacy_notice", ["NO", "NOT_SURE"],
       {"tracker": 3}, "19 Historical posts"),
]

QUESTION_INDEX: Dict[str, Dict[str, Any]] = {q["id"]: q for q in QUESTIONS}

# Ordered section list used by the frontend renderer
SECTIONS: List[str] = []
for _question in QUESTIONS:
    if _question["section"] not in SECTIONS:
        SECTIONS.append(_question["section"])

# The 20 privacy areas required by the specification
PRIVACY_AREAS: List[str] = [
    "1 Profile visibility", "2 Personal-information exposure",
    "3 Contact-information exposure", "4 Location exposure",
    "5 Workplace/education exposure", "6 Birthday exposure",
    "7 Family/relationship information", "8 Post visibility",
    "9 Friend/follower controls", "10 Tagging permissions",
    "11 Third-party application access", "12 Account authentication",
    "13 MFA usage", "14 Password reuse awareness", "15 Login alerts",
    "16 Unknown connection requests", "17 Suspicious links/messages",
    "18 Photo metadata awareness", "19 Historical posts",
    "20 Social-engineering exposure",
]


def get_questionnaire() -> Dict[str, Any]:
    """Public, JSON-serialisable representation of the questionnaire."""
    return {
        "total_questions": len(QUESTIONS),
        "sections": [
            {
                "section": section,
                "questions": [q for q in QUESTIONS if q["section"] == section],
            }
            for section in SECTIONS
        ],
        "privacy_areas": PRIVACY_AREAS,
    }


def risk_value(question_id: str, answer: str) -> float:
    """Return the deterministic risk contribution [0..1] of one answer."""
    question = QUESTION_INDEX[question_id]
    for option in question["options"]:
        if option["value"] == answer:
            return float(option["risk"])
    raise ValueError(f"Invalid answer '{answer}' for question '{question_id}'")


def valid_answers(question_id: str) -> List[str]:
    return [o["value"] for o in QUESTION_INDEX[question_id]["options"]]


def area_coverage() -> Dict[str, List[str]]:
    """Map each of the 20 privacy areas to the questions that cover it."""
    coverage: Dict[str, List[str]] = {area: [] for area in PRIVACY_AREAS}
    for question in QUESTIONS:
        if question["area"] in coverage:
            coverage[question["area"]].append(question["id"])
    return coverage
