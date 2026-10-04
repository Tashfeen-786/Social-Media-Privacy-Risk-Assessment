# API Documentation

Base URL (local): `http://localhost:8000` · Interactive docs: `/docs` (Swagger) and `/redoc`.

All responses include the security headers `X-Content-Type-Options: nosniff`,
`X-Frame-Options: SAMEORIGIN`, `Referrer-Policy: no-referrer`, `Cache-Control: no-store`.
`/api/*` is rate limited (default 60 requests / 60 s per client, configurable).

## GET /api/health
```json
{"status":"ok","service":"Social Media Privacy Risk Assessment Framework","version":"2.0.0",
 "questions":58,"models":["PRIVACY ASSESSMENT SCORE (10)","PRIVACY EXPOSURE RUBRIC (8)"],
 "vision_module":true}
```

## GET /api/methodology
Returns both scoring models, their weights/caps, the risk-level thresholds and the statement
that the two models are complementary and **not** mathematically equivalent.

## GET /api/privacy-areas
The 20 required privacy areas and the question ids covering each one.

## GET /api/sample-profile?name=demo_oversharer|demo_hardened
Returns a bundled **synthetic** `profile` + `posts` pair for the data contract.

## GET /api/questionnaire
Returns all sections/questions with answer options and their risk values, plus `categories`,
`weights`, `risk_levels`, `disclaimer` and `privacy_notice`.

## GET /api/demo-profile
Fictional synthetic demonstration answers (safe to submit).

## GET /api/improvements
List of simulator improvement keys and labels.

## POST /api/assessment → 201
Request:
```json
{ "answers": { "A1": "PUBLIC", "B1": "PUBLIC", "G1": "NO", "...": "..." },
  "weights": { "account_security": 0.20 },
  "save": true }
```
Response (abridged):
```json
{ "assessment_id": "SMPRA-1A2B3C4D5E6F",
  "created_at": "2026-09-29T19:02:11+00:00",
  "overall_score": 85.56, "risk_level": "CRITICAL",
  "category_scores": { "profile_exposure": 100.0, "account_security": 94.16, "...": 0 },
  "score_breakdown": [ { "label": "Account Security", "score": 94.16, "weight_percent": 15.0,
                         "contribution": 14.12, "level": "CRITICAL" } ],
  "top_contributors": [ { "question_id": "G1", "weighted_risk": 2.0, "text": "..." } ],
  "findings": [ { "finding_type": "mfa_disabled", "category": "account_security",
                  "severity": "CRITICAL", "finding": "Multi-factor authentication disabled",
                  "explanation": "...", "recommended_action": "..." } ],
  "recommendations": [ { "priority": "IMMEDIATE", "recommendation": "..." } ],
  "priority_summary": { "IMMEDIATE": 11, "IMPORTANT": 20, "GOOD PRACTICE": 17 },
  "security_controls_enabled": 0, "security_controls_total": 8,
  "exposure_rubric": { "model": "B", "name": "PRIVACY EXPOSURE RUBRIC", "score": 93.3,
      "risk_level": "CRITICAL",
      "categories": [ { "key": "pii", "label": "PII Exposure", "points": 22.0,
                        "max_points": 25, "capped": false, "percent_of_cap": 88.0 } ],
      "formula": "final_score = min(100, sum(min(category_points, category_cap)))" },
  "disclaimer": "This is an educational privacy-risk framework..." }
```

`weights` overrides Model-A category weights; `rubric_caps` overrides Model-B category caps.
Errors: `422` invalid/unknown answer, sensitive field submitted, or fewer than 60% of questions answered.

## GET /api/assessment/{id}
Returns the **privacy-minimised stored record** only: id, overall score, risk level, created_at,
category scores, finding types/severities. `400` malformed id, `404` not found.

## GET /api/assessment/{id}/recommendations
Recommendations linked to the stored findings.

## DELETE /api/assessment/{id}
Erases the assessment (user control / right to erasure). `200` or `404`.

## POST /api/assessment/simulate-improvement
Request:
```json
{ "answers": { "...": "..." }, "improvements": ["enable_mfa","make_phone_private"] }
```
Response:
```json
{ "simulation_type": "FRAMEWORK SIMULATION",
  "current_score": 85.56, "current_risk_level": "CRITICAL",
  "changes_applied": [ { "key": "enable_mfa", "label": "Enable multi-factor authentication (MFA)",
                         "answer_changes": { "G1": { "from": "NO", "to": "YES" } } } ],
  "new_score": 44.40, "new_risk_level": "HIGH",
  "risk_reduction": 41.16, "risk_reduction_percent": 48.11,
  "findings_before": 46, "findings_after": 26 }
```

## POST /api/assessment/report?fmt=html|pdf
Same body as `/api/assessment`; returns the generated report file. Reports are scanned by
`assert_no_sensitive_data()` before being written.

## POST /api/analyze   *(data contract)*
Request:
```json
{ "profile": { "platform": "instagram", "username": "demo.oversharer",
               "bio": "...", "privacy": {"account_private": false},
               "links": ["https://linktr.ee/demo.oversharer"],
               "site_meta": {"third_party_scripts": ["google-analytics.js"]} },
  "posts": [ { "id": "p1", "text": "Daily 7am run", "geo": {"lat": 12.97, "lon": 77.59},
               "media": {"is_child_present": true, "exif": {"created_local": "..."} } } ] }
```
Returns the 8-category rubric with a human-readable reason **and a specific fix** for every
finding. No scraping, no network calls, nothing stored.

## POST /api/upload   *(data contract)*
`multipart/form-data` with `profile` and `posts` JSON files (max 2 MB each). Parsed in memory,
never written to disk (verified by test SEC-20).

## GET /api/stats
Aggregate snapshot kept per the data contract (same payload as `/api/dashboard/stats`).

## GET /api/dashboard/stats
`total_assessments`, `average_score`, `average_exposure_score`, `risk_distribution`,
`category_averages`, `rubric_averages`, `top_weaknesses`, `recent_assessments` — all anonymised
aggregates, labelled `data_notice: "SYNTHETIC / DEMONSTRATION DATA"`.

## GET /api/privacy-checklist?fmt=json|html
The 18-item printable Social Media Privacy Checklist.

## GET /api/database/schema
Live SQLite schema plus the explicit `never_stored` list.

## POST /api/photo-metadata?count_faces=true|false  *(optional module)*
`multipart/form-data` with `file`. Processes the image **locally in memory**, returns EXIF that is
explicitly present (camera, timestamps, GPS presence) and privacy warnings. Max 8 MB. The image is
never uploaded anywhere and never stored; metadata removal (`strip_metadata_to_copy`) always
writes a sanitised **copy**. With `count_faces=true` the optional OpenCV helper returns a face
**count** only — no recognition, no identification, no age inference.

## curl examples
```bash
curl http://localhost:8000/api/health
curl http://localhost:8000/api/demo-profile > demo.json
python -c "import json;d=json.load(open('demo.json'));json.dump({'answers':d['answers']},open('body.json','w'))"
curl -X POST http://localhost:8000/api/assessment -H "Content-Type: application/json" -d @body.json
curl -X POST "http://localhost:8000/api/assessment/report?fmt=pdf" -H "Content-Type: application/json" -d @body.json -o report.pdf
```
