# Step-by-Step Implementation Guide

The ten implementation steps from the project specification, and exactly where each one lives
in this repository.

## Step 1 — Scope, Threat Model & Architecture
**What / why:** define a defensive framework that analyses *voluntarily supplied* profile data
and questionnaire answers, flags risky content and settings, assigns a score and outputs fixes.
Profiles leak PII, location trails, routine patterns and children's images — a repeatable
assessment makes privacy hygiene practical.
**Where:** `docs/THREAT_MODEL.md`, `docs/PRIVACY_RISK_MATRIX.md`,
`screenshots/02_architecture_diagram.png`, `backend/app.py`.
**Deviation (deliberate, ethical):** the specification mentions an optional scraper proxy. This
project **never** scrapes; it uses file inputs and self-reported answers only, which is also what
the specification recommends for class use.

## Step 2 — Data Contract & Sample Inputs
**What / why:** one platform-independent schema for profile metadata and posts.
**Where:** `backend/models/profile_schema.py`, synthetic samples in
`data/samples/demo_oversharer/` and `data/samples/demo_hardened/`, served by
`GET /api/sample-profile`.

```json
{ "platform": "instagram", "username": "demo.oversharer",
  "bio": "...", "website": "...", "email": "...", "phone": "...",
  "location": "...", "privacy": {"account_private": false, "show_activity": true,
  "allow_message_requests": true}, "links": ["..."],
  "site_meta": {"has_privacy_policy": false, "third_party_scripts": ["..."]} }
```

```json
[ {"id":"p1","text":"...","created_at":"...","hashtags":["#5k"],"mentions":[],
   "geo":{"lat":12.97,"lon":77.59},
   "media":{"type":"image","has_faces":true,"is_child_present":true,
            "exif":{"make":"Apple","model":"iPhone 14","created_local":"..."}}} ]
```

All sample values are fictional and use `.invalid` / reserved example ranges.

## Step 3 — Risk Rubric & Weights
**What / why:** transparent, explainable scoring.
**Where:** `backend/models/categories.py` (`RUBRIC_WEIGHTS`), `docs/METHODOLOGY.md`.

PII 25 · Geolocation/EXIF 20 · Children/minors 15 · Workplace/school 10 · Weak privacy settings 10
· Linkage 10 · Handle reuse 5 · Trackers 5 → `final = min(100, Σ capped)`.
The 10-category weighted model (Model A) is kept **alongside** this rubric, not replaced.

## Step 4 — Python Risk Engine (rules + keyword checks)
**What / why:** a fast, transparent baseline before any ML.
**Where:** `backend/services/exposure_rubric.py` — `score_profile(profile, posts)` implements the
regex/keyword rules (e-mail, phone, geo, EXIF, routine hints, child hints, workplace words,
privacy settings, aggregator links, handle comparison, declared trackers) and
`calculate_exposure_rubric(answers)` maps the questionnaire onto the same rubric.
Model A lives in `backend/services/scoring_engine.py` + `assessment_engine.py`.

## Step 5 — FastAPI Service
**Where:** `backend/app.py`, `backend/routes/api.py`.
Implements `/api/analyze`, `/api/upload`, `/api/stats` from the specification **plus** the
required assessment API (`/api/assessment`, `/api/assessment/{id}`,
`/api/assessment/{id}/recommendations`, `/api/assessment/simulate-improvement`,
`/api/dashboard/stats`, `/api/privacy-checklist`, `DELETE /api/assessment/{id}`).
Storage is SQLite via `backend/models/database.py` — **scores and finding types only**, never raw
content, usernames or platform handles (a privacy improvement over the sample schema).

## Step 6 — React Dashboard (awareness + remediation)
**Where:** `frontend-react/` (React 18 + Vite 5 + Recharts) on `http://localhost:5173`:
Home, Assessment (questionnaire → results → simulator), Dashboard, File Analyzer (upload
profile/posts, score bar, findings with fixes, aggregate snapshot).
A dependency-free static frontend (`frontend/`, Chart.js vendored locally) is also served by the
backend on `:8000` for environments without Node.js.

## Step 7 — Optional Vision Check (faces)
**Where:** `backend/services/vision_check.py`, exposed via
`POST /api/photo-metadata?count_faces=true`.
OpenCV Haar cascades **count** faces locally; images are never stored or uploaded.
**Hard limits:** no recognition, no identification, no age inference — enforced by test SEC-19.
Many small faces plus child-related captions is treated as a *hint* only.

## Step 8 — Batch CLI & Report Export
**Where:** `scripts/batch_assess.py` → `reports/privacy_report.csv` (one row per synthetic sample
folder with the exposure score, level, finding count and all eight rubric contributions).
Per-assessment HTML/PDF reports: `backend/services/report_generator.py`.

## Step 9 — Evaluation & Calibration
**Where:** `scripts/calibrate.py` — builds a benchmark, computes the mean absolute error of the
shipped weights and grid-searches three influential weights to minimise MAE.
**Honesty note:** the reference ratings are **synthetic** (an independent unweighted-mean
heuristic), so the script demonstrates the *method* and reports a genuine MAE; it does not claim
an empirically validated model and never silently changes the shipped defaults.

## Step 10 — Safety, Ethics & Extensions
**Consent:** analyse only self-owned or synthetic profiles. **Storage:** no raw text or images are
retained — only derived scores and finding types. **Explainability:** every finding carries a
human-readable reason and a specific fix; every score carries its contribution breakdown.
**Extensions (documented, not built):** browser helper that reads platform privacy settings
without scraping content; breach checks using hash search only; family-safe mode with stronger
child weighting; organisation policy templates.
**Never:** scraping, enumeration, tracking, invasive monitoring or attack content.
