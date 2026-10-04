# Final Verification Record (v2.0)

Workflow executed: **READ COMPLETE PDF → PLAN → BUILD → EXECUTE → TEST → FIX → GENERATE EVIDENCE
→ VERIFY → CLEAN → PACKAGE → ZIP → EXTRACT TO FRESH DIRECTORY → RE-RUN → VERIFY AGAIN**.

## Requirement verification

| # | Requirement | Result | Evidence |
|---|---|---|---|
| 1 | Complete folder structure | ✅ backend / frontend / frontend-react / data / reports / tests / screenshots / docs / scripts | `screenshots/01_project_structure.png` |
| 2 | All required source files exist | ✅ 5 service engines + models + routes + utils | project tree |
| 3 | Dataset generated / verified | ✅ 1,200 records, 69 columns, seed 42 | `screenshots/23_synthetic_dataset.png` |
| 4 | Backend starts | ✅ Uvicorn on :8000, startup complete | executed |
| 5 | Frontend starts | ✅ Vite React on :5173 (+ static UI on :8000) | executed |
| 6 | API tested | ✅ 14 endpoint groups exercised, correct 200/201/400/404/413/422 codes | `docs/API_DOCUMENTATION.md`, TC-51…TC-56 |
| 7 | Questionnaire works | ✅ 58 questions, 10 sections, 20/20 areas covered | TC-43, TC-44 |
| 8 | 10-category scoring (Model A) | ✅ weighted mean verified against manual calculation | TC-25, TC-26 |
| 9 | 8-category rubric (Model B) | ✅ caps 25/20/15/10/10/10/5/5 = 100, `min(100, Σ)` | TC-35, TC-36 |
| 10 | Children/minors assessment | ✅ 3 questions + 15-point dimension, no child PII collected | TC-39, SEC-18 |
| 11 | Tracker assessment | ✅ declaration-based, 5-point cap, disclaimer returned | TC-40, TC-53 |
| 12 | Linkage risk | ✅ aggregator + linked-document rules, 10-point cap | TC-40, TC-37 |
| 13 | Handle correlation | ✅ 5-point cap, self-reported + file rule | TC-41 |
| 14 | Improvement simulator | ✅ both models, per-category deltas | TC-31, screenshots 15–17 |
| 15 | All tests run | ✅ **76 passed, 0 failed** | `docs/TEST_RESULTS.md`, screenshots 24–25 |
| 16 | Screenshots verified | ✅ 27 of 29 generated + 1 bonus; 27–28 marked manual | `screenshots/README.md` |
| 17 | README verified | ✅ every required section present | `screenshots/29_readme_preview.png` |
| 18 | Report verified | ✅ 30+ sections incl. 20 areas and both models | `docs/PROJECT_REPORT.md` |
| 19 | No secrets | ✅ static scan clean, `.env` absent, `.env.example` present | SEC-13 |
| 20 | No unnecessary sensitive storage | ✅ raw-file + schema scans clean | TC-33, SEC-09, SEC-10, SEC-15 |
| 21 | Clean ZIP | ✅ no venv / node_modules / dist / __pycache__ / .pytest_cache / nested zip | packaging step |

## Executed results

| Scenario | Model A | Level | Model B | Findings |
|---|---|---|---|---|
| Fully private synthetic profile | 0.00 | LOW | 0.00 | 0 |
| Demonstration profile | 84.48 | CRITICAL | 93.30 | 51 |
| After the 9 specification improvements | 56.72 | HIGH | 71.80 | 39 |
| After all 20 improvements | 28.11 | MODERATE | 22.00 | 19 |
| Fully public synthetic profile | 100.00 | CRITICAL | 100.00 | 58 |
| Synthetic population mean (n=1,200) | 44.54 | — | 52.30 | — |
| Rule engine — `demo_oversharer` | — | CRITICAL | 100.00 | 26 |
| Rule engine — `demo_hardened` | — | LOW | 0.00 | 0 |

Calibration (synthetic reference ratings, n=120): MAE with shipped weights **1.269**,
best grid-search candidate **1.051** — defaults intentionally left unchanged.

## Defects found during execution and fixed

| # | Defect | Fix | Re-verified |
|---|---|---|---|
| 1 | Legacy v1 SQLite file lacked `exposure_score` / `exposure_level` → HTTP 500 on `/api/assessment` and `/api/dashboard/stats` | Added forward migrations in `PrivacyDatabase.init_db()` (`ALTER TABLE … ADD COLUMN`) | both endpoints 200/201; TC-32 passes |
| 2 | Persona bias produced no LOW/MODERATE synthetic records | Re-balanced persona answer-probability vectors | distribution 345/175/345/335 |
| 3 | Privacy scanner flagged ISO timestamps as phone numbers | `strip_timestamps()` + stricter phone pattern in `utils/privacy_scan.py` | SEC-09, TC-33 pass |
| 4 | Finding-type string `password_reuse` matched a naive password check | Narrowed to `password: <value>`; documented in the test | TC-33 passes |
| 5 | Evidence script used `column` / nested quoting unavailable on all shells | Replaced with portable inline Python formatters | screenshots 23, 26 regenerated |
| 6 | Sticky navigation overlapped element screenshots | Capture-time style override (`position: static`) in the Playwright script | screenshots 10–20 re-captured |
| 7 | README initially quoted unverified simulator numbers | Replaced with actually measured values (84.48 → 56.72 / 28.11) | verified against live engine output |

## Fresh-extraction re-run (packaged artefact)

See the transcript in the final response: the ZIP is extracted to a clean directory, the dataset
is regenerated, the database is seeded, **76 tests run and pass**, the demo assessment reproduces
84.48 / CRITICAL and 93.30 / CRITICAL, the backend serves all pages on :8000, the React build
succeeds and the Vite preview serves :5173.
