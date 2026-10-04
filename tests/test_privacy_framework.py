"""
test_privacy_framework.py
-------------------------
Functional test-suite (MODEL A + MODEL B).

Covers every scenario required by the project specification, including the
8-category exposure rubric, children/minors, trackers, linkage risk, handle
correlation, rubric caps, API validation, API error handling and deletion.
"""

import os

import pytest

from backend.models.categories import (
    DEFAULT_WEIGHTS,
    RUBRIC_CATEGORIES,
    RUBRIC_WEIGHTS,
    classify_risk_level,
)
from backend.models.database import PrivacyDatabase
from backend.models.questions import PRIVACY_AREAS, QUESTIONS, area_coverage
from backend.services.assessment_engine import (
    ValidationError,
    calculate_privacy_risk,
    validate_answers,
)
from backend.services.exposure_rubric import calculate_exposure_rubric, score_profile
from backend.services.improvement_simulator import RECOMMENDED_SET, simulate_improvement
from backend.services.report_generator import generate_html_report, generate_pdf_report
from backend.services.scoring_engine import extract_privacy_features
from backend.utils.privacy_scan import scan


def _score(answers):
    return calculate_privacy_risk(answers)


def _with(base, **overrides):
    answers = dict(base)
    answers.update(overrides)
    return answers


# ==========================================================================
# TC-01 / TC-02  baseline profiles
# ==========================================================================
def test_tc01_fully_private_profile(private_answers, record):
    result = _score(private_answers)
    passed = (result["overall_score"] <= 20 and result["risk_level"] == "LOW"
              and result["exposure_rubric"]["score"] == 0)
    record("TC-01", "Fully private synthetic profile", "all lowest-risk answers",
           "Model A <= 20 / LOW and Model B = 0",
           f"A={result['overall_score']} {result['risk_level']}, "
           f"B={result['exposure_rubric']['score']}", passed)
    assert passed


def test_tc02_fully_public_profile(public_answers, record):
    result = _score(public_answers)
    passed = (result["overall_score"] >= 71 and result["risk_level"] == "CRITICAL"
              and result["exposure_rubric"]["score"] == 100)
    record("TC-02", "Fully public synthetic profile", "all highest-risk answers",
           "Model A >= 71 / CRITICAL and Model B = 100",
           f"A={result['overall_score']} {result['risk_level']}, "
           f"B={result['exposure_rubric']['score']}", passed)
    assert passed


# ==========================================================================
# TC-03 .. TC-24  individual risk drivers
# ==========================================================================
@pytest.mark.parametrize("tid,scenario,qid,risky,finding,category", [
    ("TC-03", "Public phone", "B1", "PUBLIC", "public_phone", "personal_information"),
    ("TC-04", "Public e-mail", "B2", "PUBLIC", "public_email", "personal_information"),
    ("TC-05", "Public birthday", "B3", "PUBLIC", "public_birthday", "personal_information"),
    ("TC-06", "Public location", "C1", "PUBLIC", "public_location", "location_exposure"),
    ("TC-07", "Real-time check-ins", "C2", "YES", "realtime_location", "location_exposure"),
    ("TC-08", "Travel plans", "C3", "YES", "travel_plans", "location_exposure"),
    ("TC-09", "Workplace exposure", "B4", "PUBLIC", "public_workplace", "personal_information"),
    ("TC-10", "Education exposure", "B5", "PUBLIC", "public_education", "personal_information"),
    ("TC-11", "Public posts", "D1", "PUBLIC", "public_posts", "content_exposure"),
    ("TC-12", "Unknown connections", "E1", "OFTEN", "unknown_connections", "connection_risk"),
    ("TC-13", "Tag review disabled", "F1", "NO", "tag_review_disabled", "tagging_risk"),
    ("TC-14", "MFA disabled", "G1", "NO", "mfa_disabled", "account_security"),
    ("TC-15", "Login alerts disabled", "G2", "NO", "login_alerts_disabled", "account_security"),
    ("TC-16", "Password reuse reported", "G3", "YES", "password_reuse", "account_security"),
    ("TC-17", "Third-party apps not reviewed", "H1", "NEVER", "apps_not_reviewed",
     "third_party_risk"),
    ("TC-18", "Suspicious-link awareness low", "I2", "NO", "low_phishing_awareness",
     "social_engineering"),
    ("TC-19", "Old posts not reviewed", "D2", "NEVER", "old_posts_not_reviewed",
     "content_exposure"),
    ("TC-20", "Privacy settings not reviewed", "J3", "NEVER", "privacy_settings_not_reviewed",
     "digital_footprint"),
    ("TC-21", "Children/minors media public", "D6", "PUBLIC", "child_media_public",
     "content_exposure"),
    ("TC-22", "Tracker awareness low", "J7", "NO", "tracker_awareness_low", "digital_footprint"),
    ("TC-23", "Linkage risk (linked docs with PII)", "J6", "YES", "linked_docs_pii",
     "digital_footprint"),
    ("TC-24", "Handle reuse across platforms", "J4", "YES", "handle_reuse", "digital_footprint"),
])
def test_individual_risk_drivers(tid, scenario, qid, risky, finding, category,
                                 private_answers, record):
    baseline = _score(private_answers)
    result = _score(_with(private_answers, **{qid: risky}))
    types = [f["finding_type"] for f in result["findings"]]
    higher = result["category_scores"][category] > baseline["category_scores"][category]
    passed = finding in types and higher and result["overall_score"] > baseline["overall_score"]
    record(tid, scenario, f"{qid}={risky} on an otherwise private profile",
           f"finding '{finding}' raised and {category} increases",
           f"present={finding in types}, {category}: "
           f"{baseline['category_scores'][category]} -> {result['category_scores'][category]}, "
           f"overall {baseline['overall_score']} -> {result['overall_score']}", passed)
    assert passed


# ==========================================================================
# TC-25 / TC-26  scoring mechanics (Model A)
# ==========================================================================
def test_tc25_category_score_calculation(demo_answers, record):
    features = extract_privacy_features(demo_answers)
    result = _score(demo_answers)
    scores = result["category_scores"]
    passed = (len(scores) == 10 and all(0 <= v <= 100 for v in scores.values())
              and scores["account_security"] > 70
              and abs(scores["profile_exposure"]
                      - features["category_raw"]["profile_exposure"] * 100) < 0.01)
    record("TC-25", "Category score calculation (Model A)", "demo profile answers",
           "10 categories, each 0-100, matching the feature model",
           f"{len(scores)} categories, account_security={scores['account_security']}", passed)
    assert passed


def test_tc26_overall_score_calculation(demo_answers, record):
    result = _score(demo_answers)
    manual = sum(result["category_scores"][k] * DEFAULT_WEIGHTS[k] for k in DEFAULT_WEIGHTS)
    passed = abs(manual - result["overall_score"]) < 0.05 and 0 <= result["overall_score"] <= 100
    record("TC-26", "Overall weighted score calculation", "demo profile answers",
           f"weighted sum == overall score ({round(manual, 2)})",
           f"engine={result['overall_score']}", passed)
    assert passed


# ==========================================================================
# TC-27 .. TC-29  risk level boundaries
# ==========================================================================
def test_tc27_boundary_20(record):
    passed = (classify_risk_level(20) == "LOW" and classify_risk_level(20.01) == "MODERATE"
              and classify_risk_level(21) == "MODERATE")
    record("TC-27", "Score boundary 20 (LOW/MODERATE)", "scores 20, 20.01, 21",
           "20=LOW, >20=MODERATE",
           f"{classify_risk_level(20)}, {classify_risk_level(20.01)}, "
           f"{classify_risk_level(21)}", passed)
    assert passed


def test_tc28_boundary_40(record):
    passed = classify_risk_level(40) == "MODERATE" and classify_risk_level(41) == "HIGH"
    record("TC-28", "Score boundary 40 (MODERATE/HIGH)", "scores 40, 41",
           "40=MODERATE, 41=HIGH",
           f"{classify_risk_level(40)}, {classify_risk_level(41)}", passed)
    assert passed


def test_tc29_boundary_70(record):
    passed = (classify_risk_level(70) == "HIGH" and classify_risk_level(71) == "CRITICAL"
              and classify_risk_level(100) == "CRITICAL")
    record("TC-29", "Score boundary 70 (HIGH/CRITICAL)", "scores 70, 71, 100",
           "70=HIGH, 71=CRITICAL, 100=CRITICAL",
           f"{classify_risk_level(70)}, {classify_risk_level(71)}, "
           f"{classify_risk_level(100)}", passed)
    assert passed


# ==========================================================================
# TC-30 / TC-31  recommendations & simulation
# ==========================================================================
def test_tc30_recommendation_generation(demo_answers, record):
    result = _score(demo_answers)
    recs = result["recommendations"]
    immediate = [r for r in recs if r["priority"] == "IMMEDIATE"]
    covered = {r["category"] for r in recs}
    has_mfa = any("multi-factor" in r["recommendation"].lower() for r in recs)
    passed = len(recs) >= 10 and len(immediate) >= 3 and has_mfa and len(covered) >= 8
    record("TC-30", "Recommendation generation", "demo profile with MFA disabled",
           "prioritised recommendations incl. MFA advice across >=8 categories",
           f"{len(recs)} recs, {len(immediate)} IMMEDIATE, {len(covered)} categories, "
           f"mfa={has_mfa}", passed)
    assert passed


def test_tc31_improvement_simulation(demo_answers, record):
    sim = simulate_improvement(demo_answers, RECOMMENDED_SET)
    passed = (sim["new_score"] < sim["current_score"] and sim["risk_reduction"] > 0
              and sim["findings_after"] < sim["findings_before"]
              and sim["new_exposure_score"] <= sim["current_exposure_score"]
              and len(sim["category_deltas"]) == 10)
    record("TC-31", "Privacy improvement simulation (specification set)",
           f"{len(RECOMMENDED_SET)} improvements on the demo profile",
           "both model scores drop and category deltas are returned",
           f"A {sim['current_score']} -> {sim['new_score']}, "
           f"B {sim['current_exposure_score']} -> {sim['new_exposure_score']}, "
           f"findings {sim['findings_before']} -> {sim['findings_after']}", passed)
    assert passed


# ==========================================================================
# TC-32 / TC-33  database
# ==========================================================================
def test_tc32_database_save(demo_answers, record, tmp_path):
    db = PrivacyDatabase(str(tmp_path / "t.db"))
    result = _score(demo_answers)
    db.save_assessment(result)
    stored = db.get_assessment(result["assessment_id"])
    passed = (stored is not None and stored["overall_score"] == result["overall_score"]
              and len(stored["category_scores"]) == 10
              and len(stored["exposure_rubric_scores"]) == 8
              and stored["exposure_score"] == result["exposure_rubric"]["score"]
              and len(stored["findings"]) == len(result["findings"]))
    record("TC-32", "Database save & retrieve (both models)", "save demo assessment to SQLite",
           "10 category scores + 8 rubric scores + all findings retrievable",
           f"categories={len(stored['category_scores'])}, "
           f"rubric={len(stored['exposure_rubric_scores'])}, "
           f"findings={len(stored['findings'])}", passed)
    assert passed


def test_tc33_sensitive_data_not_stored(demo_answers, record, tmp_path):
    db = PrivacyDatabase(str(tmp_path / "t2.db"))
    db.save_assessment(_score(demo_answers))
    blob = open(str(tmp_path / "t2.db"), "rb").read().decode("latin-1").lower()
    # "password_reuse" is a finding-type label, not a secret; real secrets are
    # detected by the "password: <value>" pattern inside scan().
    banned = ["phone_number", "email_address", "birth_date", "home_address",
              "latitude", "longitude", "child_name"]
    hits = [b for b in banned if b in blob]
    hits += [f"{k}:{v}" for k, v in scan(blob).items() if v]
    columns = [c["name"].lower() for t in db.schema_info() for c in t["columns"]]
    bad_columns = [c for c in columns
                   if any(k in c for k in ["phone", "email", "address", "birth", "password"])]
    passed = not hits and not bad_columns
    record("TC-33", "Sensitive data is not stored", "inspect raw SQLite file and schema",
           "no sensitive values or columns present",
           f"value_hits={hits}, sensitive_columns={bad_columns}", passed)
    assert passed


# ==========================================================================
# TC-34  report generation
# ==========================================================================
def test_tc34_report_generation(demo_answers, record, tmp_path):
    result = _score(demo_answers)
    html_path = generate_html_report(result, str(tmp_path))
    pdf_path = generate_pdf_report(result, str(tmp_path))
    html = open(html_path, encoding="utf-8").read()
    passed = (os.path.getsize(pdf_path) > 1000 and result["assessment_id"] in html
              and "Disclaimer" in html and "Privacy Checklist" in html
              and "Privacy Exposure Rubric" in html)
    record("TC-34", "Privacy report generation (HTML + PDF, both models)",
           "demo assessment result",
           "both files created; contain id, rubric, checklist and disclaimer",
           f"html={os.path.getsize(html_path)}B, pdf={os.path.getsize(pdf_path)}B", passed)
    assert passed


# ==========================================================================
# TC-35 .. TC-41  the 8-category exposure rubric (MODEL B)
# ==========================================================================
def test_tc35_rubric_categories_and_weights(record):
    passed = (len(RUBRIC_CATEGORIES) == 8 and sum(RUBRIC_WEIGHTS.values()) == 100
              and RUBRIC_WEIGHTS["pii"] == 25 and RUBRIC_WEIGHTS["geo"] == 20
              and RUBRIC_WEIGHTS["child"] == 15 and RUBRIC_WEIGHTS["work"] == 10
              and RUBRIC_WEIGHTS["privacy"] == 10 and RUBRIC_WEIGHTS["link"] == 10
              and RUBRIC_WEIGHTS["handle"] == 5 and RUBRIC_WEIGHTS["tracker"] == 5)
    record("TC-35", "8-category rubric definition", "RUBRIC_WEIGHTS",
           "PII 25, GEO 20, CHILD 15, WORK 10, PRIV 10, LINK 10, HANDLE 5, TRACK 5 = 100",
           f"{RUBRIC_WEIGHTS} total={sum(RUBRIC_WEIGHTS.values())}", passed)
    assert passed


def test_tc36_rubric_caps_enforced(public_answers, record):
    rubric = calculate_exposure_rubric(public_answers)
    over_cap = [c for c in rubric["categories"] if c["points"] > c["max_points"]]
    any_capped = [c["key"] for c in rubric["categories"] if c["capped"]]
    passed = not over_cap and rubric["score"] == 100 and len(any_capped) >= 1
    record("TC-36", "Rubric per-category caps and min(100, sum)",
           "fully public profile (raw points exceed caps)",
           "no category exceeds its cap and final score is capped at 100",
           f"score={rubric['score']}, capped_categories={any_capped}", passed)
    assert passed


def test_tc37_rubric_file_engine_oversharer(sample_files, record):
    profile, posts = sample_files["demo_oversharer"]
    result = score_profile(profile, posts)
    cats = {c["key"]: c["points"] for c in result["categories"]}
    passed = (result["score"] > 70 and cats["pii"] > 0 and cats["geo"] > 0
              and cats["child"] > 0 and cats["work"] > 0 and cats["privacy"] > 0
              and cats["link"] > 0 and cats["handle"] > 0 and cats["tracker"] > 0
              and all(f.get("fix") for f in result["findings"]))
    record("TC-37", "File-driven rubric on the synthetic oversharer sample",
           "data/samples/demo_oversharer/{profile,posts}.json",
           "all 8 categories contribute and every finding has a fix",
           f"score={result['score']}, categories={cats}", passed)
    assert passed


def test_tc38_rubric_file_engine_hardened(sample_files, record):
    profile, posts = sample_files["demo_hardened"]
    result = score_profile(profile, posts)
    passed = result["score"] == 0 and result["risk_level"] == "LOW" and not result["findings"]
    record("TC-38", "File-driven rubric on the synthetic hardened sample",
           "data/samples/demo_hardened/{profile,posts}.json",
           "score 0, LOW, no findings",
           f"score={result['score']} {result['risk_level']}, "
           f"findings={len(result['findings'])}", passed)
    assert passed


def test_tc39_children_rubric_category(private_answers, record):
    answers = _with(private_answers, D6="PUBLIC", D7="PUBLIC", D8="PUBLIC")
    rubric = calculate_exposure_rubric(answers)
    child = next(c for c in rubric["categories"] if c["key"] == "child")
    baseline = calculate_exposure_rubric(private_answers)
    passed = child["points"] == 15 and child["max_points"] == 15 and baseline["score"] == 0
    record("TC-39", "Children / minors exposure category",
           "D6/D7/D8 = PUBLIC on an otherwise private profile",
           "child category reaches but does not exceed its 15-point cap",
           f"child points={child['points']}/{child['max_points']}", passed)
    assert passed


def test_tc40_tracker_and_linkage_categories(private_answers, record):
    answers = _with(private_answers, J5="YES", J6="YES", J7="NO", J8="NO")
    rubric = calculate_exposure_rubric(answers)
    link = next(c for c in rubric["categories"] if c["key"] == "link")
    tracker = next(c for c in rubric["categories"] if c["key"] == "tracker")
    passed = link["points"] == 10 and tracker["points"] == 5
    record("TC-40", "Linkage risk and third-party tracker categories",
           "J5/J6=YES, J7/J8=NO", "link=10/10 and tracker=5/5",
           f"link={link['points']}, tracker={tracker['points']}", passed)
    assert passed


def test_tc41_handle_correlation_category(private_answers, record):
    rubric = calculate_exposure_rubric(_with(private_answers, J4="YES"))
    handle = next(c for c in rubric["categories"] if c["key"] == "handle")
    passed = handle["points"] == 5 and handle["max_points"] == 5
    record("TC-41", "Reuse / handle correlation category", "J4=YES",
           "handle category = 5/5 points", f"handle={handle['points']}", passed)
    assert passed


def test_tc42_models_are_independent(demo_answers, record):
    result = _score(demo_answers)
    model_a = result["overall_score"]
    model_b = result["exposure_rubric"]["score"]
    passed = (model_a != model_b and 0 <= model_a <= 100 and 0 <= model_b <= 100
              and "not mathematically equivalent" in result["methodology"]["relationship"].lower()
              or "complementary" in result["methodology"]["relationship"].lower())
    record("TC-42", "Two models coexist and are documented as complementary",
           "demo profile scored by both models",
           "both scores present, methodology explains they are not equivalent",
           f"Model A={model_a}, Model B={model_b}", passed)
    assert passed


# ==========================================================================
# TC-43 .. TC-50  framework guarantees, API validation and error handling
# ==========================================================================
def test_tc43_questionnaire_size_and_sections(record):
    sections = {q["section"] for q in QUESTIONS}
    passed = len(QUESTIONS) >= 40 and len(sections) == 10
    record("TC-43", "Questionnaire size and coverage", "backend.models.questions",
           ">= 40 questions across the 10 sections A-J",
           f"{len(QUESTIONS)} questions, {len(sections)} sections", passed)
    assert passed


def test_tc44_all_20_privacy_areas_covered(record):
    coverage = area_coverage()
    uncovered = [area for area, qs in coverage.items() if not qs]
    passed = len(PRIVACY_AREAS) == 20 and not uncovered
    record("TC-44", "All 20 required privacy areas are covered", "area_coverage()",
           "20 areas, each mapped to >= 1 question",
           f"areas={len(PRIVACY_AREAS)}, uncovered={uncovered}", passed)
    assert passed


def test_tc45_input_validation_rejects_bad_input(record):
    errors = 0
    bad_payloads = [{"A1": "MAYBE"}, {"ZZ9": "PUBLIC"}, {"phone": "9999999999"},
                    "notadict", {"A1": "PUBLIC"}, {"child_name": "x"}]
    for bad in bad_payloads:
        try:
            validate_answers(bad)
        except ValidationError:
            errors += 1
    passed = errors == len(bad_payloads)
    record("TC-45", "Input validation", f"{len(bad_payloads)} malformed payloads",
           "all rejected with ValidationError", f"{errors}/{len(bad_payloads)} rejected", passed)
    assert passed


def test_tc46_weights_are_configurable(demo_answers, record):
    default = _score(demo_answers)
    custom = calculate_privacy_risk(demo_answers, {"account_security": 0.60})
    total = sum(custom["weights_used"].values())
    passed = (abs(total - 1.0) < 0.001 and custom["weights_used"]["account_security"] > 0.4
              and custom["overall_score"] != default["overall_score"])
    record("TC-46", "Configurable Model-A weights", "account_security weight override 0.60",
           "weights renormalise to 1.0 and change the score",
           f"sum={round(total, 4)}, score {default['overall_score']} -> "
           f"{custom['overall_score']}", passed)
    assert passed


def test_tc47_rubric_caps_are_configurable(demo_answers, record):
    default = _score(demo_answers)
    custom = calculate_privacy_risk(demo_answers, rubric_caps={"pii": 5})
    pii = next(c for c in custom["exposure_rubric"]["categories"] if c["key"] == "pii")
    passed = pii["max_points"] == 5 and pii["points"] <= 5 and \
        custom["exposure_rubric"]["score"] <= default["exposure_rubric"]["score"]
    record("TC-47", "Configurable Model-B caps", "pii cap override 25 -> 5",
           "pii contribution limited to the new cap",
           f"pii={pii['points']}/{pii['max_points']}, "
           f"B {default['exposure_rubric']['score']} -> "
           f"{custom['exposure_rubric']['score']}", passed)
    assert passed


def test_tc48_scoring_is_deterministic(demo_answers, record):
    first, second = _score(demo_answers), _score(demo_answers)
    passed = (first["overall_score"] == second["overall_score"]
              and first["category_scores"] == second["category_scores"]
              and first["exposure_rubric"]["score"] == second["exposure_rubric"]["score"])
    record("TC-48", "Deterministic & explainable scoring", "same answers scored twice",
           "identical scores in both models",
           f"{first['overall_score']}=={second['overall_score']}, "
           f"{first['exposure_rubric']['score']}=={second['exposure_rubric']['score']}", passed)
    assert passed


def test_tc49_partial_submission_rejected(private_answers, record):
    partial = dict(list(private_answers.items())[:10])
    try:
        calculate_privacy_risk(partial)
        raised = False
    except ValidationError:
        raised = True
    record("TC-49", "Minimum answer coverage enforced",
           f"only 10 of {len(QUESTIONS)} questions answered",
           "ValidationError raised", f"raised={raised}", raised)
    assert raised


def test_tc50_findings_have_full_structure(demo_answers, record):
    result = _score(demo_answers)
    keys = {"category", "severity", "finding", "explanation", "recommended_action"}
    complete = all(keys.issubset(f.keys()) for f in result["findings"])
    severities = {f["severity"] for f in result["findings"]}
    passed = complete and severities.issubset({"CRITICAL", "HIGH", "MEDIUM", "LOW"})
    record("TC-50", "Finding structure completeness", "demo profile findings",
           "every finding has category/severity/finding/explanation/action",
           f"complete={complete}, severities={sorted(severities)}", passed)
    assert passed


# ==========================================================================
# TC-51 .. TC-56  API behaviour
# ==========================================================================
def test_tc51_api_create_assessment(client, demo_answers, record):
    response = client.post("/api/assessment", json={"answers": demo_answers, "save": True})
    body = response.json()
    passed = (response.status_code == 201 and "exposure_rubric" in body
              and len(body["category_scores"]) == 10
              and len(body["exposure_rubric"]["categories"]) == 8)
    record("TC-51", "API POST /api/assessment", "demo answers",
           "HTTP 201 with both model results",
           f"HTTP {response.status_code}, A={body.get('overall_score')}, "
           f"B={body.get('exposure_rubric', {}).get('score')}", passed)
    assert passed


def test_tc52_api_error_handling(client, record):
    cases = {
        "unknown id (400)": (client.get("/api/assessment/not-an-id").status_code, 400),
        "missing id (404)": (client.get("/api/assessment/SMPRA-AAAAAAAAAAAA").status_code, 404),
        "bad answer (422)": (client.post("/api/assessment",
                                         json={"answers": {"A1": "NOPE"}}).status_code, 422),
        "bad sample (404)": (client.get("/api/sample-profile?name=nope_none").status_code, 404),
    }
    passed = all(actual == expected for actual, expected in cases.values())
    record("TC-52", "API error handling", "4 malformed / missing-resource requests",
           "400, 404, 422, 404 respectively",
           ", ".join(f"{k}={v[0]}" for k, v in cases.items()), passed)
    assert passed


def test_tc53_api_analyze_endpoint(client, sample_files, record):
    profile, posts = sample_files["demo_oversharer"]
    response = client.post("/api/analyze", json={"profile": profile, "posts": posts})
    body = response.json()
    passed = (response.status_code == 200 and body["score"] > 70
              and len(body["categories"]) == 8 and "tracker_disclaimer" in body)
    record("TC-53", "API POST /api/analyze (data contract)", "synthetic oversharer files",
           "HTTP 200 with 8 rubric categories and tracker disclaimer",
           f"HTTP {response.status_code}, score={body.get('score')}", passed)
    assert passed


def test_tc54_api_upload_endpoint(client, record):
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    folder = os.path.join(root, "data", "samples", "demo_oversharer")
    with open(os.path.join(folder, "profile.json"), "rb") as pf, \
         open(os.path.join(folder, "posts.json"), "rb") as qf:
        response = client.post("/api/upload", files={
            "profile": ("profile.json", pf, "application/json"),
            "posts": ("posts.json", qf, "application/json")})
    body = response.json()
    passed = response.status_code == 200 and body["score"] > 70
    record("TC-54", "API POST /api/upload (two JSON files)", "synthetic sample upload",
           "HTTP 200 with a rubric score",
           f"HTTP {response.status_code}, score={body.get('score')}", passed)
    assert passed


def test_tc55_api_delete_assessment(client, demo_answers, record):
    created = client.post("/api/assessment", json={"answers": demo_answers, "save": True})
    aid = created.json()["assessment_id"]
    deleted = client.delete(f"/api/assessment/{aid}")
    after = client.get(f"/api/assessment/{aid}")
    passed = deleted.status_code == 200 and after.status_code == 404
    record("TC-55", "API DELETE /api/assessment/{id}", "create then delete then fetch",
           "delete 200 then get 404",
           f"delete={deleted.status_code}, get={after.status_code}", passed)
    assert passed


def test_tc56_api_dashboard_and_checklist(client, record):
    stats = client.get("/api/dashboard/stats")
    checklist = client.get("/api/privacy-checklist")
    checklist_html = client.get("/api/privacy-checklist?fmt=html")
    body = stats.json()
    items = checklist.json()["items"]
    passed = (stats.status_code == 200 and "rubric_averages" in body
              and body["data_notice"] == "SYNTHETIC / DEMONSTRATION DATA"
              and len(items) >= 21 and checklist_html.status_code == 200)
    record("TC-56", "Dashboard stats + privacy checklist endpoints",
           "GET /api/dashboard/stats and /api/privacy-checklist",
           "stats include rubric averages + synthetic notice; checklist >= 21 items",
           f"stats={stats.status_code}, items={len(items)}, "
           f"notice={body.get('data_notice')}", passed)
    assert passed
