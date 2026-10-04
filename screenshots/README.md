# Evidence & Screenshot Checklist (29 required items + 1 bonus)

All evidence in this folder corresponds to **real, executed functionality**. Nothing is mocked,
hand-drawn to look like application output, or fabricated. Only synthetic / demo data appears in
any image — no personal information, passwords, API keys, tokens or real people's data.

**Evidence types**

* **A — Automatically generated local evidence** — rendered from genuine command output or real
  project files (`scripts/generate_local_evidence.py`).
* **B — Browser / application evidence** — real Playwright screenshots of the running
  **React + Vite** UI (`:5173`) and the FastAPI backend (`:8000`), captured at 1600×1000 with
  device scale 1.5 → 2400×1500 px (`scripts/capture_screenshots.py`).
* **C — Account-dependent evidence** — requires *your* accounts.
  **MANUAL USER ACTION REQUIRED.** Never fabricated by this project.

| # | Filename | What it proves | Type | Status | In ZIP |
|---|---|---|---|---|---|
| 1 | `01_project_structure.png` | Complete project tree from a real `find` listing | A | auto-generated | ✅ |
| 2 | `02_architecture_diagram.png` | System architecture incl. both scoring models and the data contract | A | auto-generated | ✅ |
| 3 | `03_privacy_assessment_homepage.png` | Homepage: two models, 20 privacy areas, ethical scope | B | browser capture | ✅ |
| 4 | `04_questionnaire.png` | 58-question questionnaire with the synthetic demo profile loaded | B | browser capture | ✅ |
| 5 | `05_profile_privacy_section.png` | CATEGORY A — Profile Visibility questions | B | browser capture | ✅ |
| 6 | `06_personal_information_section.png` | CATEGORY B — Personal Information (visibility only, no PII) | B | browser capture | ✅ |
| 7 | `07_location_section.png` | CATEGORY C — Location Privacy incl. EXIF question | B | browser capture | ✅ |
| 8 | `08_account_security_section.png` | CATEGORY G — Authentication & Account Security | B | browser capture | ✅ |
| 9 | `09_social_engineering_section.png` | CATEGORY I — Messaging & Social Engineering | B | browser capture | ✅ |
| 10 | `10_overall_risk_score.png` | Result cards: Model A score, level, Model B rubric, controls | B | browser capture | ✅ |
| 11 | `11_category_scores.png` | 10-category score table with weights and contributions | B | browser capture | ✅ |
| 12 | `12_privacy_risk_chart.png` | Privacy risk radar (Model A) + rubric bar chart (Model B) | B | browser capture | ✅ |
| 13 | `13_top_findings.png` | Findings table: severity, category, explanation, action | B | browser capture | ✅ |
| 14 | `14_recommendations.png` | Prioritised recommendations (IMMEDIATE / IMPORTANT / GOOD PRACTICE) | B | browser capture | ✅ |
| 15 | `15_improvement_simulator_before.png` | Simulator **before** — 84.48 CRITICAL, rubric 93.30 | B | browser capture | ✅ |
| 16 | `16_improvement_simulator_after.png` | Simulator **after** — 45.54 HIGH, rubric 34.00, comparison chart | B | browser capture | ✅ |
| 17 | `17_risk_reduction.png` | Risk-reduction panel: −38.94 points (−46.1 %), findings 51 → 32 | B | browser capture | ✅ |
| 18 | `18_privacy_dashboard.png` | Full React dashboard with SYNTHETIC / DEMONSTRATION DATA notice | B | browser capture | ✅ |
| 19 | `19_risk_distribution.png` | Privacy risk distribution chart | B | browser capture | ✅ |
| 20 | `20_top_weakness_chart.png` | Top privacy weaknesses chart | B | browser capture | ✅ |
| 21 | `21_privacy_checklist.png` | Printable 21-item Social Media Privacy Checklist | B | browser capture | ✅ |
| 22 | `22_privacy_report.png` | Generated privacy report incl. the exposure-rubric section | B | browser capture | ✅ |
| 23 | `23_synthetic_dataset.png` | Real CSV head, record count, both-model distributions | A | auto-generated | ✅ |
| 24 | `24_automated_tests.png` | Real `pytest tests/test_privacy_framework.py -v` output | A | auto-generated | ✅ |
| 25 | `25_privacy_security_tests.png` | Real `pytest tests/test_security_privacy.py -v` output | A | auto-generated | ✅ |
| 26 | `26_database_schema.png` | Real SQLite `.schema` incl. `exposure_rubric_scores` + row counts | A | auto-generated | ✅ |
| 27 | `27_github_commits.png` | GitHub commit history | **C** | **MANUAL USER ACTION REQUIRED** | ❌ |
| 28 | `28_github_repository.png` | GitHub repository page | **C** | **MANUAL USER ACTION REQUIRED** | ❌ |
| 29 | `29_readme_preview.png` | README.md preview | A | auto-generated | ✅ |
| 30 | `30_file_analyzer_exposure_rubric.png` | *(bonus)* File Analyzer running the 8-category rubric over the synthetic `demo_oversharer` export | B | browser capture | ✅ |

**27 of the 29 required items are present.** Items 27 and 28 depend on your GitHub account and
have deliberately **not** been fabricated.

---

## Manual capture instructions

### 27 — `27_github_commits.png`  (MANUAL USER ACTION REQUIRED)
1. Follow `docs/GITHUB_SETUP.md` to create the repository and push the project.
2. Open `https://github.com/<your-username>/Social-Media-Privacy-Risk-Assessment/commits/main`.
3. Capture the full browser window (≥1440×900) showing commit messages and dates.
4. Save as `screenshots/27_github_commits.png`.

### 28 — `28_github_repository.png`  (MANUAL USER ACTION REQUIRED)
1. Open `https://github.com/<your-username>/Social-Media-Privacy-Risk-Assessment`.
2. Ensure the description, topics, folder listing and rendered README are visible.
3. Capture the full browser window and save as `screenshots/28_github_repository.png`.

> Do not include your e-mail address, tokens or private repository data in these captures.

---

## Regenerating all evidence yourself

```bat
REM Windows - three windows
scripts\start_backend.bat            REM window 1  -> :8000
scripts\start_frontend.bat           REM window 2  -> :5173
scripts\generate_evidence.bat        REM window 3
```

```bash
# any OS
python -m uvicorn backend.app:app --port 8000 &
(cd frontend-react && npm run dev &)
python scripts/run_demo_assessment.py
python scripts/batch_assess.py
python scripts/generate_local_evidence.py
python -m playwright install chromium
python scripts/capture_screenshots.py
```

## Generation record for the current images

* Backend executed on `:8000`, React + Vite frontend on `:5173`.
* Demo assessment: **Model A 84.48 / CRITICAL**, **Model B 93.30 / CRITICAL**, 51 findings.
* Simulator capture (12 improvements selected in the browser): **45.54 / HIGH**, rubric **34.00**,
  findings 51 → 32.
* Dashboard seeded with 300 synthetic assessments; dataset 1,200 records / 69 columns.
* Test suite at capture time: **76 passed, 0 failed**.
