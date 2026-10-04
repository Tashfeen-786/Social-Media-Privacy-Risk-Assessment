# Privacy by Design — Implementation Evidence

Each principle below is implemented in code, with the file that proves it.

| Principle | Implementation | Evidence |
|---|---|---|
| **Data Minimisation** | Only `assessment_id`, overall score, risk level, category scores, finding types and timestamps are persisted. Raw answers never touch the database. | `backend/models/database.py` (schema), test `SEC-10` |
| **Purpose Limitation** | Stored records are used exclusively for the user's own report and anonymised aggregates; no secondary use, no export to third parties. | `backend/models/database.py::dashboard_stats`, `backend/routes/api.py` |
| **Least Privilege** | Aggregate endpoints are read-only; admin-style operations require `ADMIN_API_KEY`; the API accepts only whitelisted answer values. | `backend/utils/security.py::admin_key_valid`, test `SEC-07` |
| **Privacy by Default** | No accounts, no cookies, no trackers, no analytics, no third-party CDN (Chart.js is vendored locally). Saving is explicit (`save` flag). | `frontend/`, `backend/routes/api.py` |
| **Transparency** | Weights, thresholds, per-category contributions and per-question contributions are returned with every assessment; the disclaimer is shown in UI, API and report. | `backend/services/scoring_engine.py::score_breakdown`, `/api/questionnaire` |
| **User Control** | `DELETE /api/assessment/{id}` erases a record; reports are local files the user owns; the demo profile lets users explore without entering anything. | `backend/routes/api.py`, test `SEC-12` |
| **Retention Limitation** | Nothing identifying is retained, so nothing needs to expire; the database can be deleted at any time without data loss for the user. | `.gitignore` excludes `*.db`; `docs/SECURITY_PRIVACY_TESTING.md` |
| **Secure Processing** | Strict input validation with an explicit forbidden-field list, HTML escaping, security headers, rate limiting, secrets only from environment variables, report sensitive-data guard. | `backend/services/assessment_engine.py::FORBIDDEN_FIELDS`, `backend/utils/security.py`, `backend/utils/privacy_scan.py` |

## Data flow (what exists where)

```
Browser  ──answers (in memory only)──►  API  ──scores/findings──►  SQLite
                                        │
                                        └──report file (local disk, no PII)
```

Raw answers exist only for the duration of one HTTP request. They are validated, converted to
numeric features, scored, and discarded.

## Forbidden input fields (rejected with HTTP 422)

`phone, phone_number, mobile, email, email_address, address, home_address, birthdate, birth_date,
dob, date_of_birth, password, passwd, pin, otp, ssn, aadhaar, credit_card, latitude, longitude,
gps, messages, message_content, child_name, school_name, full_name`

## Additional Privacy-by-Design controls (v2.0)

| Control | Implementation | Test |
|---|---|---|
| Children's data is never requested | Child questions ask visibility only; `child_name` is a forbidden field | SEC-18 |
| Uploaded profile/posts files are never stored | `/api/upload` parses in memory and writes nothing to disk | SEC-20 |
| Vision helper cannot identify anyone | `vision_check.py` only calls `detectMultiScale` (face **count**) | SEC-19 |
| No scraping or outbound crawling | static scan proves no HTTP client / scraper imports in `backend/` | SEC-16 |
| No account enumeration | no lookup/search-user/enumeration endpoints exist | SEC-17 |
| Tracker check is declaration-based | reads only `site_meta.third_party_scripts` from the supplied file; contacts no website | TC-37 |
