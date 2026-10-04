"""
test_security_privacy.py
------------------------
Security and privacy verification tests (API level).

Verifies that the application does not unnecessarily store sensitive data and
that basic security controls (validation, XSS defence, rate limiting,
authorisation concept, safe report generation, deletion) actually work.
"""

import os
import re

from backend.models.database import PrivacyDatabase
from backend.services.assessment_engine import calculate_privacy_risk, demo_profile_answers
from backend.services.report_generator import assert_no_sensitive_data, build_report_html
from backend.utils.privacy_scan import scan
from backend.utils.security import (
    RATE_LIMIT_REQUESTS,
    admin_key_valid,
    rate_limit_check,
    reset_rate_limits,
    sanitize_text,
    valid_assessment_id,
)


def test_sec01_api_health_and_headers(client, record):
    response = client.get("/api/health")
    headers = response.headers
    passed = (response.status_code == 200
              and headers.get("x-content-type-options") == "nosniff"
              and headers.get("x-frame-options") == "SAMEORIGIN"
              and "no-store" in headers.get("cache-control", ""))
    record("SEC-01", "Security response headers", "GET /api/health",
           "200 + nosniff, SAMEORIGIN, no-store headers",
           f"{response.status_code}, {dict(list(headers.items()))['x-content-type-options']}",
           passed)
    assert passed


def test_sec02_api_rejects_invalid_answers(client, record):
    response = client.post("/api/assessment", json={"answers": {"A1": "<script>x</script>"}})
    passed = response.status_code == 422
    record("SEC-02", "API input validation", 'POST /api/assessment with a script payload',
           "HTTP 422", f"HTTP {response.status_code}", passed)
    assert passed


def test_sec03_sensitive_fields_rejected(client, record):
    answers = demo_profile_answers()
    answers["phone"] = "9999999999"
    response = client.post("/api/assessment", json={"answers": answers})
    passed = response.status_code == 422 and "sensitive" in response.text.lower()
    record("SEC-03", "Sensitive field submission blocked", "answers payload containing 'phone'",
           "HTTP 422 with a privacy message", f"HTTP {response.status_code}", passed)
    assert passed


def test_sec04_xss_payload_not_reflected(client, record):
    payload = "<img src=x onerror=alert(1)>"
    response = client.get(f"/api/assessment/{payload}")
    passed = response.status_code == 400 and "<img" not in response.text
    record("SEC-04", "XSS / injection payload not reflected",
           "GET /api/assessment/<img src=x onerror=...>",
           "HTTP 400 and payload not echoed back",
           f"HTTP {response.status_code}, reflected={'<img' in response.text}", passed)
    assert passed


def test_sec05_output_sanitisation(record):
    cleaned = sanitize_text("<script>alert('x')</script>")
    passed = "<script>" not in cleaned and "&lt;script&gt;" in cleaned
    record("SEC-05", "Output escaping helper", "<script>alert('x')</script>",
           "HTML-escaped string", cleaned[:60], passed)
    assert passed


def test_sec06_rate_limiting(record):
    reset_rate_limits()
    allowed = sum(1 for _ in range(RATE_LIMIT_REQUESTS + 10) if rate_limit_check("1.2.3.4"))
    reset_rate_limits()
    passed = allowed == RATE_LIMIT_REQUESTS
    record("SEC-06", "API rate limiting", f"{RATE_LIMIT_REQUESTS + 10} rapid requests",
           f"only {RATE_LIMIT_REQUESTS} allowed", f"{allowed} allowed", passed)
    assert passed


def test_sec07_authorisation_concept(record):
    os.environ["ADMIN_API_KEY"] = "secret-test-key"
    passed = (admin_key_valid("secret-test-key") and not admin_key_valid("wrong")
              and not admin_key_valid(None))
    record("SEC-07", "Authorisation key check", "valid / invalid / missing admin key",
           "only the configured key is accepted",
           f"valid=True wrong={admin_key_valid('wrong')} none={admin_key_valid(None)}", passed)
    assert passed


def test_sec08_assessment_id_validation(record):
    good = valid_assessment_id("SMPRA-ABCDEF123456")
    bad = any(valid_assessment_id(v) for v in ["../../etc/passwd", "1 OR 1=1", "SMPRA-;DROP"])
    passed = good and not bad
    record("SEC-08", "Identifier validation (path traversal / SQLi strings)",
           "valid id + 3 malicious ids", "only the valid id accepted",
           f"good={good}, malicious_accepted={bad}", passed)
    assert passed


def test_sec09_no_sensitive_data_persisted(client, record, tmp_path):
    db = PrivacyDatabase(str(tmp_path / "sec.db"))
    for _ in range(3):
        db.save_assessment(calculate_privacy_risk(demo_profile_answers()))
    raw = open(str(tmp_path / "sec.db"), "rb").read().decode("latin-1")
    hits = {name: value for name, value in scan(raw).items() if value}
    passed = not hits
    record("SEC-09", "No sensitive data in the database file",
           "3 saved assessments, raw file scanned",
           "no phone/email/DOB/password patterns", str(hits), passed)
    assert passed


def test_sec10_raw_answers_not_persisted(record, tmp_path):
    db = PrivacyDatabase(str(tmp_path / "sec2.db"))
    result = calculate_privacy_risk(demo_profile_answers())
    db.save_assessment(result)
    columns = [c["name"] for t in db.schema_info() for c in t["columns"]]
    passed = not any(c.startswith(("A", "B", "C", "D", "E", "F", "G", "H", "I", "J"))
                     and len(c) <= 3 for c in columns)
    record("SEC-10", "Raw questionnaire answers are not persisted", "schema column inspection",
           "no per-question answer columns", f"columns={columns}", passed)
    assert passed


def test_sec11_report_contains_no_sensitive_data(record):
    result = calculate_privacy_risk(demo_profile_answers())
    html = build_report_html(result)
    try:
        assert_no_sensitive_data(html)
        clean = True
    except ValueError:
        clean = False
    record("SEC-11", "Safe report generation", "generated HTML report scanned",
           "no phone / e-mail / DOB / password patterns", f"clean={clean}", clean)
    assert clean


def test_sec12_data_deletion(client, record):
    response = client.post("/api/assessment",
                           json={"answers": demo_profile_answers(), "save": True})
    assessment_id = response.json()["assessment_id"]
    deleted = client.delete(f"/api/assessment/{assessment_id}")
    after = client.get(f"/api/assessment/{assessment_id}")
    passed = deleted.status_code == 200 and after.status_code == 404
    record("SEC-12", "Data deletion / right to erasure",
           "POST then DELETE then GET the same assessment",
           "delete 200, subsequent get 404",
           f"delete={deleted.status_code}, get={after.status_code}", passed)
    assert passed


def test_sec13_environment_variables_not_hardcoded(record):
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    offenders = []
    for folder, _, files in os.walk(os.path.join(root, "backend")):
        for name in files:
            if not name.endswith(".py"):
                continue
            text = open(os.path.join(folder, name), encoding="utf-8").read()
            if re.search(r"(api_key|secret|password)\s*=\s*['\"][A-Za-z0-9]{8,}['\"]",
                         text, re.I):
                offenders.append(name)
    env_example = os.path.exists(os.path.join(root, ".env.example"))
    no_env_committed = not os.path.exists(os.path.join(root, ".env"))
    passed = not offenders and env_example and no_env_committed
    record("SEC-13", "Secrets handled via environment variables",
           "static scan of backend/*.py + .env checks",
           "no hardcoded secrets, .env.example present, no .env committed",
           f"offenders={offenders}, env_example={env_example}, no_env={no_env_committed}", passed)
    assert passed


def test_sec14_privacy_notice_exposed(client, record):
    data = client.get("/api/questionnaire").json()
    notice = data.get("privacy_notice", "")
    passed = "never asks" in notice.lower() and "disclaimer" in data
    record("SEC-14", "Transparency: privacy notice and disclaimer exposed",
           "GET /api/questionnaire", "privacy notice + disclaimer present",
           f"notice_len={len(notice)}", passed)
    assert passed


def test_sec16_no_scraping_or_network_calls(record):
    """The codebase must contain no HTTP client calls to external services."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    offenders = []
    patterns = re.compile(
        r"(requests\.(get|post)|urllib\.request\.urlopen|httpx\.(get|post)|"
        r"aiohttp\.|selenium|BeautifulSoup|scrapy)", re.I)
    for folder, _, files in os.walk(os.path.join(root, "backend")):
        for name in files:
            if name.endswith(".py"):
                text = open(os.path.join(folder, name), encoding="utf-8").read()
                if patterns.search(text):
                    offenders.append(name)
    record("SEC-16", "No scraping / outbound crawling in the backend",
           "static scan of backend/*.py for HTTP clients and scrapers",
           "no requests/urllib/httpx/selenium/BeautifulSoup/scrapy usage",
           f"offenders={offenders}", not offenders)
    assert not offenders


def test_sec17_no_account_enumeration(record):
    """No endpoint may look up accounts by name/handle on a remote platform."""
    from backend.routes.api import router
    paths = [route.path for route in router.routes]
    suspicious = [p for p in paths if any(word in p.lower()
                  for word in ["lookup", "search-user", "enumerate", "profile-of", "osint"])]
    record("SEC-17", "No account-enumeration endpoints", "inspect all API routes",
           "no lookup/enumeration style endpoints exist",
           f"routes={len(paths)}, suspicious={suspicious}", not suspicious)
    assert not suspicious


def test_sec18_child_data_never_collected(client, record):
    """Child-related questions must ask only about visibility, never identity."""
    from backend.models.questions import QUESTIONS
    child_questions = [q for q in QUESTIONS if "child" in (q.get("finding_type") or "")]
    banned_words = ["name of", "which school", "child's name", "address"]
    offenders = [q["id"] for q in child_questions
                 if any(word in q["text"].lower() for word in banned_words)]
    api = client.post("/api/assessment", json={"answers": {"child_name": "x"}})
    passed = bool(child_questions) and not offenders and api.status_code == 422
    record("SEC-18", "Children's personal data is never requested or accepted",
           f"{len(child_questions)} child-related questions + child_name payload",
           "questions ask visibility only; child_name rejected with 422",
           f"offenders={offenders}, api={api.status_code}", passed)
    assert passed


def test_sec19_vision_module_is_count_only(record):
    """The optional OpenCV helper must count faces only - never identify."""
    from backend.services import vision_check
    source = open(vision_check.__file__, encoding="utf-8").read().lower()
    banned = ["face_recognition", "recognize", "encodings", "identify(", "compare_faces"]
    offenders = [b for b in banned if b in source]
    has_count = "detectmultiscale" in source
    record("SEC-19", "Vision helper performs face COUNT only",
           "static inspection of backend/services/vision_check.py",
           "detectMultiScale present, no recognition/identification APIs",
           f"count={has_count}, offenders={offenders}", has_count and not offenders)
    assert has_count and not offenders


def test_sec20_uploaded_files_not_persisted(client, record, tmp_path):
    """Uploaded profile/posts JSON must not be written to disk."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    before = set(os.listdir(os.path.join(root, "data")))
    folder = os.path.join(root, "data", "samples", "demo_oversharer")
    with open(os.path.join(folder, "profile.json"), "rb") as pf, \
         open(os.path.join(folder, "posts.json"), "rb") as qf:
        response = client.post("/api/upload", files={
            "profile": ("profile.json", pf, "application/json"),
            "posts": ("posts.json", qf, "application/json")})
    after = set(os.listdir(os.path.join(root, "data")))
    new_files = after - before
    passed = response.status_code == 200 and not new_files
    record("SEC-20", "Uploaded files are processed in memory, never stored",
           "POST /api/upload then inspect data/ directory",
           "HTTP 200 and no new files written",
           f"http={response.status_code}, new_files={sorted(new_files)}", passed)
    assert passed


def test_sec15_stored_record_fields_minimal(client, record):
    response = client.post("/api/assessment",
                           json={"answers": demo_profile_answers(), "save": True})
    stored = client.get(f"/api/assessment/{response.json()['assessment_id']}").json()
    allowed = {"assessment_id", "overall_score", "risk_level", "created_at",
               "category_scores", "findings", "category_labels", "disclaimer",
               "exposure_score", "exposure_level", "exposure_rubric_scores",
               "rubric_labels"}
    extra = set(stored) - allowed
    passed = not extra
    record("SEC-15", "Data minimisation of stored records", "GET /api/assessment/{id}",
           "only minimal privacy-safe fields returned", f"unexpected_fields={extra}", passed)
    assert passed
