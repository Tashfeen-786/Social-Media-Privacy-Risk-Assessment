"""
conftest.py
-----------
Shared pytest fixtures + the test-evidence recorder.

Every test can call:
    record(test_id, scenario, input_summary, expected, actual, passed)

At the end of the session the recorder writes a genuine result matrix to
    docs/TEST_RESULTS.md
Nothing is fabricated: rows are only written when the test actually runs.
"""

import os
import sys
from datetime import datetime, timezone

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

os.environ.setdefault("DATABASE_PATH", os.path.join(ROOT, "data", "test_privacy_assessment.db"))
os.environ.setdefault("ADMIN_API_KEY", "test-admin-key")

_RECORDS = []


@pytest.fixture
def record():
    def _record(test_id, scenario, test_input, expected, actual, passed):
        _RECORDS.append({
            "id": test_id, "scenario": scenario, "input": str(test_input)[:160],
            "expected": str(expected)[:120], "actual": str(actual)[:120],
            "result": "PASS" if passed else "FAIL",
        })
    return _record


@pytest.fixture(scope="session")
def client():
    from fastapi.testclient import TestClient

    from backend.app import app
    return TestClient(app)


@pytest.fixture
def demo_answers():
    from backend.services.assessment_engine import demo_profile_answers
    return demo_profile_answers()


@pytest.fixture
def private_answers():
    from backend.services.assessment_engine import hardened_profile_answers
    return hardened_profile_answers()


@pytest.fixture
def public_answers():
    from backend.services.assessment_engine import fully_public_answers
    return fully_public_answers()


@pytest.fixture
def sample_files():
    """Bundled SYNTHETIC profile.json / posts.json samples."""
    import json
    samples = {}
    base = os.path.join(ROOT, "data", "samples")
    for name in sorted(os.listdir(base)):
        folder = os.path.join(base, name)
        if not os.path.isdir(folder):
            continue
        with open(os.path.join(folder, "profile.json"), encoding="utf-8") as handle:
            profile = json.load(handle)
        with open(os.path.join(folder, "posts.json"), encoding="utf-8") as handle:
            posts = json.load(handle)
        samples[name] = (profile, posts)
    return samples


def pytest_sessionfinish(session, exitstatus):
    if not _RECORDS:
        return
    docs = os.path.join(ROOT, "docs")
    os.makedirs(docs, exist_ok=True)
    passed = sum(1 for r in _RECORDS if r["result"] == "PASS")
    lines = [
        "# Automated Test Results",
        "",
        f"_Generated automatically by pytest on "
        f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}._",
        "",
        f"**Total recorded scenarios: {len(_RECORDS)} | Passed: {passed} | "
        f"Failed: {len(_RECORDS) - passed} | pytest exit status: {exitstatus}**",
        "",
        "| Test ID | Scenario | Input | Expected Result | Actual Result | Pass/Fail |",
        "|---|---|---|---|---|---|",
    ]
    for r in sorted(_RECORDS, key=lambda x: x["id"]):
        lines.append(f"| {r['id']} | {r['scenario']} | `{r['input']}` | {r['expected']} | "
                     f"{r['actual']} | **{r['result']}** |")
    lines.append("")
    with open(os.path.join(docs, "TEST_RESULTS.md"), "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
