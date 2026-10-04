# Security & Privacy Testing

All results in `docs/TEST_RESULTS.md` are produced by actually running
`python -m pytest tests -v`. Nothing in that file is hand-written.

**Current run: 76 tests, 76 passed, 0 failed.**

## What is verified

### Privacy (data minimisation proven, not claimed)
| Check | Method | Test |
|---|---|---|
| No phone numbers stored | raw SQLite file scanned with regex detectors | SEC-09, TC-29 |
| No e-mail addresses stored | same | SEC-09, TC-29 |
| No home addresses / coordinates stored | schema + value scan | SEC-09, TC-29 |
| No birth dates stored | date-pattern scan (ISO timestamps excluded) | SEC-09 |
| No passwords stored | `password: <value>` pattern scan | SEC-09 |
| No private messages stored | schema inspection — no such column exists | SEC-10 |
| Raw questionnaire answers not persisted | schema column inspection | SEC-10 |
| Stored record fields are minimal | API response field whitelist | SEC-15 |
| Reports contain no sensitive data | generated HTML scanned before write | SEC-11 |
| Sensitive fields rejected at the API | `phone` field submitted → 422 | SEC-03 |

### Security
| Check | Method | Test |
|---|---|---|
| Input validation | malformed/unknown/oversized answers rejected | SEC-02, TC-32 |
| XSS protection | script payload in a path parameter is not reflected; all UI output escaped | SEC-04, SEC-05 |
| Security headers | nosniff / SAMEORIGIN / no-referrer / no-store asserted | SEC-01 |
| Rate limiting | 70 rapid calls → exactly 60 allowed | SEC-06 |
| Authorisation concept | only the configured `ADMIN_API_KEY` accepted | SEC-07 |
| Identifier validation | traversal and SQLi-style ids rejected | SEC-08 |
| Secrets management | static scan for hardcoded secrets; `.env.example` present, `.env` absent | SEC-13 |
| Safe report generation | sensitive-pattern guard raises before writing | SEC-11 |
| Data deletion | POST → DELETE → GET returns 404 | SEC-12 |
| Transparency | privacy notice + disclaimer exposed by the API | SEC-14 |
| No scraping / crawling | static scan: no requests/urllib/httpx/selenium/bs4/scrapy in backend | SEC-16 |
| No account enumeration | no lookup/search-user/enumeration routes exist | SEC-17 |
| Children's data never collected | child questions ask visibility only; `child_name` → 422 | SEC-18 |
| Vision helper is count-only | no recognition/identification APIs in `vision_check.py` | SEC-19 |
| Uploaded files never persisted | `/api/upload` writes nothing to `data/` | SEC-20 |

## Threats intentionally out of scope
No authentication/accounts are implemented (privacy by default: there is nothing to log in to),
so session management is limited to a documented authorisation concept for admin endpoints.
TLS is expected to be terminated by the hosting platform in any real deployment.

## How to reproduce
```bash
python -m pytest tests -v
type docs\TEST_RESULTS.md      # Windows;  cat docs/TEST_RESULTS.md elsewhere
```
