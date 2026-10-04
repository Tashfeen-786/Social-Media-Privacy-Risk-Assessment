# Social Media Privacy Risk Assessment Framework

> Privacy-focused cybersecurity framework for assessing social-media exposure, account-security
> practices, social-engineering risk, digital-footprint risk, and personalized privacy
> improvements using synthetic/self-reported data.

**This project is designed for defensive cybersecurity and privacy education. It uses synthetic or
voluntarily provided assessment responses and does not scrape, track, or profile real social-media
users.**

---

## Overview

The framework turns a **58-question** self-reported privacy questionnaire (and, optionally, a
synthetic `profile.json` / `posts.json` export) into:

* **Model A — PRIVACY ASSESSMENT SCORE**: 10 weighted categories → one explainable 0–100 score
* **Model B — PRIVACY EXPOSURE RUBRIC**: 8 capped exposure dimensions → `min(100, Σ points)`
* severity-rated **findings**, prioritised **recommendations**, an **improvement simulator**,
  a **dashboard**, an exportable **privacy report** and a printable **21-item checklist**

…while storing **no personal data at all**.

| | |
|---|---|
| Questionnaire | 58 questions · 10 sections (CATEGORY A–J) · all 20 privacy areas |
| Scoring | two deterministic, fully explainable models (no black box) |
| Risk levels | LOW 0–20 · MODERATE 21–40 · HIGH 41–70 · CRITICAL 71–100 |
| Synthetic dataset | 1,200 fictional records, 69 columns, seeded |
| Automated tests | **76 executed tests** (56 functional + 20 security/privacy) — all passing |
| Personal data stored | **none** |

## Problem Statement

People cannot tell how exposed their social-media presence actually is. Privacy settings are
scattered, defaults drift towards visibility, and the link between *oversharing* and *account
takeover / social engineering* is not obvious. Existing tools either scrape profiles (intrusive,
often prohibited, and blind to non-public settings) or give generic advice that is not tied to the
user's actual configuration and cannot be measured.

## Objectives

1. Quantify social-media privacy exposure without scraping, tracking or profiling anyone.
2. Produce an explainable 0–100 score with ten category sub-scores (Model A).
3. Produce a complementary 8-dimension exposure rubric with capped contributions (Model B).
4. Generate concrete, prioritised, personalised remediation guidance.
5. Show the effect of improvements through a clearly labelled framework simulation.
6. Demonstrate Privacy-by-Design in executable code, verified by tests.
7. Provide defensive awareness material on digital footprint and social engineering.

## Cybersecurity Relevance

Security awareness · privacy engineering · GRC/risk assessment · defensive threat modelling ·
account-security controls (MFA, alerts, sessions, password hygiene) · least privilege for
third-party apps · data minimisation and purpose limitation · secure API design and testing.
Relevant roles: Cybersecurity Analyst, Privacy Analyst, GRC Analyst, SOC Analyst, Security
Consultant, IAM Analyst, Security Awareness Specialist, Privacy Engineer.

## Privacy vs Security

| Privacy | Security |
|---|---|
| Who can *see* what about you | Who can *access* your account |
| Audience settings, contact visibility, location sharing, footprint | MFA, login alerts, unique passwords, session review, connected apps |
| Failure → profiling, impersonation, targeted scams | Failure → account takeover, data theft |

A strong password and MFA do not stop a public phone number, birth date and live check-ins from
being visible. **Strong account security ≠ strong privacy** — so the framework scores both.

## Features

* 58-question questionnaire covering all 20 required privacy areas
* Input validation that **refuses** sensitive data fields (including `child_name`)
* `extract_privacy_features()` → structured numeric features and named risk flags
* `calculate_privacy_risk()` → 10 category scores + weighted overall score (Model A)
* `calculate_exposure_rubric()` / `score_profile()` → 8-category rubric (Model B)
* `generate_privacy_findings()` → 58 catalogued findings with severity, explanation and action
* `generate_recommendations()` → IMMEDIATE / IMPORTANT / GOOD PRACTICE
* `simulate_improvement()` → before → changes → after, for **both** models
* Radar + bar + doughnut + comparison charts; React dashboard and static dashboard
* HTML **and** PDF privacy report with a sensitive-data guard
* File Analyzer for the `profile.json` / `posts.json` data contract
* Optional local EXIF metadata viewer + optional OpenCV **face-count** helper
* Batch CLI (`batch_assess.py`) and weight calibration (`calibrate.py`)
* Privacy-first SQLite storage with forward migrations and anonymised aggregates
* REST API with validation, error handling, security headers and rate limiting

## Architecture

```
User (voluntary)                         profile.json / posts.json (synthetic)
  ↓                                                   ↓
Privacy Questionnaire (58 questions) → Input Validation → Feature Extraction
  ↓
Profile · Personal Info · Location/EXIF · Content+Child · Account Security ·
Social Engineering · Footprint/Link analyzers
  ↓
Category Scores (10 × 0–100)
  ↓                                   ↘
MODEL A  calculate_privacy_risk()      MODEL B  calculate_exposure_rubric()
  ↓                                   ↙
Overall Risk Score + Exposure Score + Level
  ↓
Findings Engine → Recommendation Engine → Improvement Simulator
  ↓
Privacy Dashboard · Privacy Report · Anonymised Aggregates → SQLite analytics DB
```

Diagram: `screenshots/02_architecture_diagram.png`

## Technology Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10+ · FastAPI · Uvicorn · Pydantic v2 |
| Database | SQLite (privacy-minimised schema + forward migrations) |
| Frontend (modern) | React 18 + Vite 5 + **Recharts** → `http://localhost:5173` |
| Frontend (static) | HTML/CSS/JS + Chart.js (vendored) served by the backend → `:8000` |
| Reports | HTML + ReportLab PDF |
| Optional vision | OpenCV (face **count** only, never identification) |
| Testing | pytest + FastAPI TestClient + Playwright (evidence capture) |

## Privacy Questionnaire

| Section | Category key | Questions |
|---|---|---|
| CATEGORY A: Profile Visibility | `profile_exposure` | 5 |
| CATEGORY B: Personal Information | `personal_information` | 6 |
| CATEGORY C: Location Privacy | `location_exposure` | 7 |
| CATEGORY D: Posts & Content | `content_exposure` | 8 |
| CATEGORY E: Friends / Followers | `connection_risk` | 5 |
| CATEGORY F: Tagging & Mentions | `tagging_risk` | 4 |
| CATEGORY G: Authentication & Account Security | `account_security` | 6 |
| CATEGORY H: Third-Party Apps | `third_party_risk` | 4 |
| CATEGORY I: Messaging & Social Engineering | `social_engineering` | 5 |
| CATEGORY J: Digital Footprint | `digital_footprint` | 8 |
| **Total** | | **58** |

Answer types: `PUBLIC / FRIENDS / PRIVATE / NOT SURE`, `YES / SOMETIMES / NO / NOT SURE`,
`REGULARLY / RARELY / NEVER / NOT SURE`, `NEVER / RARELY / SOMETIMES / OFTEN`.

**No question asks for actual personal data.** *"Is your phone number publicly visible?"* —
never *"What is your phone number?"*. Child-related questions ask only whether such media or
information is publicly visible; a child's name, school or address is never requested.

## 20 Privacy Areas

1 Profile visibility · 2 Personal-information exposure · 3 Contact-information exposure ·
4 Location exposure · 5 Workplace/education exposure · 6 Birthday exposure ·
7 Family/relationship information · 8 Post visibility · 9 Friend/follower controls ·
10 Tagging permissions · 11 Third-party application access · 12 Account authentication ·
13 MFA usage · 14 Password reuse awareness · 15 Login alerts · 16 Unknown connection requests ·
17 Suspicious links/messages · 18 Photo metadata awareness · 19 Historical posts ·
20 Social-engineering exposure

Live coverage map: `GET /api/privacy-areas` (verified by test TC-44).

## 10-Category Risk Scoring (Model A)

Profile Exposure · Personal Information · Location Exposure · Content Exposure · Connection Risk ·
Tagging Risk · Account Security · Third-Party App Risk · Social Engineering · Digital Footprint —
each 0–100 where **0 = lower assessed risk, 100 = higher assessed risk**.

Weights: 10 / 15 / 15 / 10 / 10 / 5 / 15 / 5 / 10 / 5 % = 100 % (configurable, renormalised).

## 8-Category Exposure Rubric (Model B)

| Exposure category | Max points |
|---|---|
| PII Exposure | 25 |
| Geolocation / EXIF leakage & routine trails | 20 |
| Children / minors in media | 15 |
| Workplace / school disclosures | 10 |
| Weak privacy settings | 10 |
| Linkage risks | 10 |
| Reuse / handle correlation | 5 |
| Third-party trackers in linked sites | 5 |
| **Total** | **100** |

`final_score = min(100, Σ min(category_points, category_cap))`

## Risk Methodology

Full write-up: **`docs/METHODOLOGY.md`**.

* Model A evaluates privacy and security **behaviours and settings**.
* Model B evaluates specific **exposure dimensions**.
* They are **complementary**, use different mathematics (weighted mean vs capped additive
  points) and will normally produce different numbers for the same person.
* Both are **educational models**. Neither guarantees real-world safety or compromise.

> **Educational framework.** Weights and thresholds are educational assumptions and should be
> validated before professional risk decisions.

## Privacy Findings

Every triggered finding carries **category, severity (CRITICAL/HIGH/MEDIUM/LOW), finding,
explanation and recommended action** — e.g. public phone number, public birthday, real-time
location sharing, travel plans, EXIF not stripped, workplace badge photos, children's media
public, unknown connections, tag review disabled, MFA disabled, password re-use, apps not
reviewed, linked documents containing PII, handle reuse, trackers unknown.

## Recommendation Engine

| Priority | Meaning | Example |
|---|---|---|
| IMMEDIATE | act now | Enable multi-factor authentication |
| IMPORTANT | act soon | Review and revoke unnecessary application access |
| GOOD PRACTICE | ongoing hygiene | Re-run this assessment every 3–6 months |

Coverage includes profile privacy, personal information, location, workplace/school,
children/minors, tagging, connections, MFA, login alerts, third-party apps, tracker awareness,
old posts, suspicious links, photo metadata, digital footprint, linkage risks and handle reuse.

## Improvement Simulator

`POST /api/assessment/simulate-improvement` re-scores the same answers with selected improvements
and returns **current → changes applied → new simulated score → risk reduction**, for both models
plus per-category deltas. Clearly labelled **FRAMEWORK SIMULATION**.

Executed demonstration result with the 9-item improvement set named in the specification
(phone, birthday, location, travel plans, unknown requests, tag review, MFA, login alerts,
third-party apps): **Model A 84.48 CRITICAL → 56.72 HIGH (−27.76, −32.9 %)**,
**Model B 93.30 → 71.80 (−21.50)**, findings 51 → 39.

Selecting **all 20** improvements reduces it further to **Model A 28.11 MODERATE** and
**Model B 22.00** (findings 51 → 19). The screenshot
`screenshots/16_improvement_simulator_after.png` shows a 12-item selection captured in the
browser: **84.48 CRITICAL → 45.54 HIGH (−38.94, −46.1 %)**, rubric **93.30 → 34.00**.

## Digital Footprint

Active vs passive footprint is explained in the report; the framework assesses only self-reported
practices: old posts, abandoned public accounts, search-engine indexing, handle reuse, link-in-bio
aggregators, linked documents and privacy-settings review cadence.

## Social Engineering

`docs/SOCIAL_ENGINEERING_AWARENESS.md` — *How oversharing can increase social-engineering risk*.
Conceptual and defensive only: **no** attack scripts, **no** pretext templates, **no**
personalised attack messages.

## Account Security

MFA, unique passwords, password manager, login alerts, recovery review, active sessions and
unknown devices. The dashboard reports "Security Controls Enabled" as *n/9*.

## Third-Party Applications

Connected apps, unused integrations, permission scopes and "sign in with social account" usage —
framed through the **principle of least privilege**.

## Children / Minors Privacy

A dedicated 15-point rubric dimension plus three questionnaire items. The framework asks only
whether child-related media, posts and school information are publicly visible. It never requests
a child's name, school, address or any other detail, and never identifies anyone. The optional
OpenCV helper **counts** faces only — no recognition, no age inference (verified by SEC-18/SEC-19).

## Tracker Awareness

A basic, **declaration-based** educational check: it reads only `site_meta.third_party_scripts`
from a supplied synthetic file, or the user's self-reported awareness. No website is crawled or
contacted, no browser is fingerprinted. This is **not** a complete browser-level tracker audit.

## Dashboard

Top cards (Model A score · risk level · Model B exposure · high-risk categories ·
recommendations · security controls) and charts: category risk scores, risk distribution, top
weaknesses, account-security controls, digital-footprint radar, improvement comparison, rubric
averages and Model A vs Model B. Aggregate data is explicitly labelled
**SYNTHETIC / DEMONSTRATION DATA**.

## Privacy Report

Assessment ID · date · overall risk · risk level · category scores · **exposure rubric** ·
top findings · recommendations · priority actions · privacy checklist · disclaimer.
Exportable as **HTML or PDF**. `assert_no_sensitive_data()` scans every report before writing.

## Privacy by Design

| Principle | How it is implemented |
|---|---|
| Data Minimisation | Only ids, scores, rubric points, finding types and timestamps are stored |
| Purpose Limitation | Stored data feeds only your report and anonymised aggregates |
| Least Privilege | Read-only aggregates; admin actions require `ADMIN_API_KEY` |
| Privacy by Default | No accounts, cookies, trackers, analytics or third-party CDNs |
| Transparency | Weights, caps, thresholds and per-question contributions exposed via API |
| User Control | `DELETE /api/assessment/{id}` erases an assessment |
| Retention Limitation | Nothing identifying is retained; uploads are never written to disk |
| Secure Processing | Validation, escaping, security headers, rate limiting, report guard |

Details and test references: `docs/PRIVACY_BY_DESIGN.md`.

## Installation

### Windows (automated)

```bat
scripts\setup_windows.bat        :: venv + backend deps + React deps
scripts\generate_dataset.bat     :: 1,200 synthetic records + seeds the DB
scripts\start_backend.bat        :: http://127.0.0.1:8000  (Swagger at /docs)
scripts\start_frontend.bat       :: http://localhost:5173  (React + Vite)
scripts\run_tests.bat            :: pytest → regenerates docs\TEST_RESULTS.md
scripts\generate_evidence.bat    :: regenerates screenshots/evidence
```

### Manual (any OS)

```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python data/generate_dataset.py --records 1200 --seed 42
python scripts/seed_database.py 300
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000     # terminal 1
cd frontend-react && npm install && npm run dev                  # terminal 2
```

* Backend + static frontend: <http://127.0.0.1:8000>
* React frontend: <http://localhost:5173>
* Swagger: <http://127.0.0.1:8000/docs>

## Usage

1. Open <http://localhost:5173> → **Start Privacy Assessment**.
2. Answer the questionnaire (≥60 % required) or click **Load demo profile**.
3. Review Model A score, Model B rubric, radar chart, findings and recommendations.
4. Tick improvements → **Run simulation** to see the framework-simulated reduction.
5. Open **Dashboard** for aggregates, **File Analyzer** for the JSON data contract,
   **Checklist** for the printable list, and download the HTML/PDF report.

## API Documentation

Interactive: <http://127.0.0.1:8000/docs> · Full reference: `docs/API_DOCUMENTATION.md`

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/assessment` | Score a questionnaire (both models) |
| GET | `/api/assessment/{id}` | Retrieve a stored minimised assessment |
| GET | `/api/assessment/{id}/recommendations` | Recommendations for an assessment |
| DELETE | `/api/assessment/{id}` | Erase an assessment |
| POST | `/api/assessment/simulate-improvement` | Improvement simulation |
| POST | `/api/assessment/report?fmt=html\|pdf` | Generate and download a report |
| GET | `/api/dashboard/stats` · `/api/stats` | Anonymised aggregates |
| GET | `/api/privacy-checklist?fmt=json\|html` | 21-item checklist |
| POST | `/api/analyze` · `/api/upload` | Rule-based exposure rubric over the data contract |
| GET | `/api/questionnaire` · `/api/methodology` · `/api/privacy-areas` | Metadata |
| GET | `/api/improvements` · `/api/demo-profile` · `/api/sample-profile` | Demo data |
| GET | `/api/database/schema` · `/api/health` | Schema + health |
| POST | `/api/photo-metadata` | Local EXIF viewer (+ optional face count) |

## Testing

```bash
python -m pytest tests -v            # or: scripts\run_tests.bat
```

**76 tests execute**: TC-01…TC-56 (functional, incl. the 8-category rubric, rubric caps,
children/minors, trackers, linkage, handle correlation, API validation, API error handling,
deletion) and SEC-01…SEC-20 (security/privacy). The matrix — Test ID · Scenario · Input ·
Expected · Actual · Pass/Fail — is written to `docs/TEST_RESULTS.md` **by the test run itself**.

## Security & Privacy Testing

Verified by executed tests: no phone numbers / e-mails / addresses / birth dates / passwords /
coordinates / private messages in the database or generated reports; raw answers never persisted;
uploaded files never stored; no scraping or outbound HTTP clients; no account-enumeration
endpoints; children's data never requested; vision helper is count-only; input validation; XSS
payloads not reflected; identifier validation; rate limiting; authorisation key; secrets via
environment variables; data deletion. See `docs/SECURITY_PRIVACY_TESTING.md`.

## Results

| Scenario | Model A | Level | Model B | Findings |
|---|---|---|---|---|
| Fully private synthetic profile | 0.00 | LOW | 0.00 | 0 |
| Demonstration profile (synthetic) | 84.48 | CRITICAL | 93.30 | 51 |
| Demo profile after the 9 specification improvements | 56.72 | HIGH | 71.80 | 39 |
| Demo profile after all 20 improvements | 28.11 | MODERATE | 22.00 | 19 |
| Fully public synthetic profile | 100.00 | CRITICAL | 100.00 | 58 |
| Synthetic population (n = 1,200) mean | 44.54 | — | 52.30 | — |
| File rule engine — `demo_oversharer` | — | CRITICAL | 100.00 | 26 |
| File rule engine — `demo_hardened` | — | LOW | 0.00 | 0 |

Population distribution (Model A): LOW 345 · MODERATE 175 · HIGH 345 · CRITICAL 335.
Tests: **76/76 passing**.

## Limitations

* Self-reported answers are unverified against the real platform configuration.
* Weights, caps and thresholds are educational assumptions, not empirically calibrated.
* Platform feature parity is assumed; some controls do not exist everywhere.
* The simulator models the framework's own re-score, not real-world attack probability.
* The rule engine sees only what the supplied synthetic export contains.
* The tracker check is declaration-based, not a browser-level audit.
* The optional face count is a coarse hint, never an identification or age judgement.
* The synthetic dataset reflects designed personas, not observed behaviour.

## Future Improvements

Platform-specific privacy checklists · configurable organisational policies · privacy-awareness
quizzes · privacy maturity scoring · family/teen safety modules · enterprise training mode ·
GRC reporting · anonymous organisational trend analysis · better risk-model calibration against
expert ratings · localisation · accessibility (WCAG AA) · report comparison over time ·
secure client-side assessment · optional local-only mode. **No** invasive monitoring or scraping.

## Screenshots

All evidence lives in `screenshots/` and is catalogued in `screenshots/README.md`
(29 required items + 1 bonus). 27 of 29 are generated automatically; items 27–28 (GitHub) are
clearly marked **MANUAL USER ACTION REQUIRED** and have deliberately not been fabricated.

## Learning Outcomes

* Designing two complementary, explainable risk models instead of one opaque score
* Applying Privacy by Design to real code and proving it with tests
* Threat modelling and risk-matrix construction for a personal (non-enterprise) asset
* Building a validated REST API with error handling, headers and rate limiting
* Writing genuine functional *and* security/privacy automated tests
* Building a React + Vite dashboard against a FastAPI backend
* Producing professional evidence, documentation and reporting

## Ethical Disclaimer

This project is designed for **defensive** cybersecurity and privacy education. It uses synthetic
or voluntarily provided assessment responses and does **not** scrape, track, or profile real
social-media users. It never requests actual phone numbers, e-mail addresses, postal addresses,
birth dates, passwords, message content or any child's personal details; it performs no account
enumeration, no privacy-setting bypass and no invasive monitoring. It contains no attack scripts
and no social-engineering templates. Both risk scores are educational and do not guarantee that
an account will or will not be compromised.

## Author

Student cybersecurity project — Social Media Privacy Risk Assessment Framework, v2.0.
Replace this section with your name, course and contact before publishing.
