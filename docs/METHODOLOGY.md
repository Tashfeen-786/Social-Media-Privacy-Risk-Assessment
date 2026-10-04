# Scoring Methodology — Two Complementary Models

The framework implements **two** educational scoring models that run on every
assessment. They are deliberately kept separate and are **not** mathematically
equivalent.

---

## A · PRIVACY ASSESSMENT SCORE (10 categories)

**What it measures:** privacy and security **behaviour and configuration**, from the
self-reported questionnaire.

**How it is computed**

```
answer_risk       ∈ [0.0 .. 1.0]                 (documented per answer option)
category_score    = Σ(answer_risk × question_weight) / Σ(question_weight) × 100
overall_score     = Σ(category_score × category_weight)
risk_level        = LOW ≤20 | MODERATE ≤40 | HIGH ≤70 | CRITICAL >70
```

**Category weights (configurable, always renormalised to 100 %)**

| Category | Weight |
|---|---|
| Profile Visibility | 10 % |
| Personal Information | 15 % |
| Location Privacy | 15 % |
| Posts & Content | 10 % |
| Connections | 10 % |
| Tagging | 5 % |
| Account Security | 15 % |
| Third-Party Apps | 5 % |
| Social Engineering | 10 % |
| Digital Footprint | 5 % |
| **Total** | **100 %** |

Override per request with `"weights": {...}` or globally via `PRIVACY_WEIGHTS_FILE`.
Weights are renormalised, so a partial override can never silently break the default model.

---

## B · PRIVACY EXPOSURE RUBRIC (8 categories)

**What it measures:** specific **exposure dimensions**, either from the questionnaire or
from a supplied synthetic `profile.json` / `posts.json` export.

**How it is computed**

```
category_points   = Σ(contributions detected in that dimension)
capped_points     = min(category_points, category_cap)
final_score       = min(100, Σ capped_points)
```

**Category caps (configurable)**

| # | Exposure category | Max points |
|---|---|---|
| 1 | PII Exposure (phone / e-mail / DOB / home information) | 25 |
| 2 | Geolocation / EXIF leakage & routine trails | 20 |
| 3 | Children / minors in media | 15 |
| 4 | Workplace / school disclosures (badges, room numbers) | 10 |
| 5 | Weak privacy settings (public account, open DMs, activity status) | 10 |
| 6 | Linkage risks (link-in-bio, public documents, repositories) | 10 |
| 7 | Reuse / handle correlation | 5 |
| 8 | Third-party trackers in linked sites | 5 |
| | **Total** | **100** |

Two entry points:

* `calculate_exposure_rubric(answers)` — questionnaire-driven (each question declares its
  rubric contribution in `backend/models/questions.py`).
* `score_profile(profile, posts)` — rule-based engine over the data contract
  (regex for e-mail/phone, geo/EXIF flags, child flags, workplace keywords, privacy settings,
  link inspection, handle comparison, declared tracker scripts).

---

## Why both models?

| | Model A | Model B |
|---|---|---|
| Input | 58-question self-report | questionnaire **or** exported synthetic files |
| Mathematics | weighted mean of category scores | capped additive points |
| Answers the question | *"How good are my habits and settings?"* | *"What specific exposure exists right now?"* |
| Sensitive to | consistent behaviour across many questions | presence of a few high-impact exposures |
| Typical divergence | a user with good habits but one public document scores low on A, higher on B | |

Because the mathematics differ, **the same person will normally get two different numbers**.
That is expected and intentional: A is a behaviour grade, B is an exposure inventory. Reading
them together is more informative than either alone — for example, `A = 35 (MODERATE)` with
`B = 62 (HIGH)` means "reasonable habits, but something specific is exposed right now".

---

## Shared limitations

* Both are **educational assumptions**, not empirically calibrated risk values.
* Neither guarantees that an account will or will not be compromised.
* Model A depends on honest, accurate self-reporting.
* Model B depends on the completeness of the supplied synthetic export.
* The tracker check is declaration-based, not a browser-level audit.
* `scripts/calibrate.py` demonstrates the calibration *method* against synthetic reference
  ratings; real calibration against expert ratings remains future work.
