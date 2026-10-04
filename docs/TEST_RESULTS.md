# Automated Test Results

_Generated automatically by pytest on 2026-09-30 02:23 UTC._

**Total recorded scenarios: 20 | Passed: 20 | Failed: 0 | pytest exit status: 0**

| Test ID | Scenario | Input | Expected Result | Actual Result | Pass/Fail |
|---|---|---|---|---|---|
| SEC-01 | Security response headers | `GET /api/health` | 200 + nosniff, SAMEORIGIN, no-store headers | 200, nosniff | **PASS** |
| SEC-02 | API input validation | `POST /api/assessment with a script payload` | HTTP 422 | HTTP 422 | **PASS** |
| SEC-03 | Sensitive field submission blocked | `answers payload containing 'phone'` | HTTP 422 with a privacy message | HTTP 422 | **PASS** |
| SEC-04 | XSS / injection payload not reflected | `GET /api/assessment/<img src=x onerror=...>` | HTTP 400 and payload not echoed back | HTTP 400, reflected=False | **PASS** |
| SEC-05 | Output escaping helper | `<script>alert('x')</script>` | HTML-escaped string | &lt;script&gt;alert(&#x27;x&#x27;)&lt;/script&gt; | **PASS** |
| SEC-06 | API rate limiting | `70 rapid requests` | only 60 allowed | 60 allowed | **PASS** |
| SEC-07 | Authorisation key check | `valid / invalid / missing admin key` | only the configured key is accepted | valid=True wrong=False none=False | **PASS** |
| SEC-08 | Identifier validation (path traversal / SQLi strings) | `valid id + 3 malicious ids` | only the valid id accepted | good=True, malicious_accepted=False | **PASS** |
| SEC-09 | No sensitive data in the database file | `3 saved assessments, raw file scanned` | no phone/email/DOB/password patterns | {} | **PASS** |
| SEC-10 | Raw questionnaire answers are not persisted | `schema column inspection` | no per-question answer columns | columns=['assessment_id', 'overall_score', 'risk_level', 'exposure_score', 'exposure_level', 'created_at', 'category_sco | **PASS** |
| SEC-11 | Safe report generation | `generated HTML report scanned` | no phone / e-mail / DOB / password patterns | clean=True | **PASS** |
| SEC-12 | Data deletion / right to erasure | `POST then DELETE then GET the same assessment` | delete 200, subsequent get 404 | delete=200, get=404 | **PASS** |
| SEC-13 | Secrets handled via environment variables | `static scan of backend/*.py + .env checks` | no hardcoded secrets, .env.example present, no .env committed | offenders=[], env_example=True, no_env=True | **PASS** |
| SEC-14 | Transparency: privacy notice and disclaimer exposed | `GET /api/questionnaire` | privacy notice + disclaimer present | notice_len=197 | **PASS** |
| SEC-15 | Data minimisation of stored records | `GET /api/assessment/{id}` | only minimal privacy-safe fields returned | unexpected_fields=set() | **PASS** |
| SEC-16 | No scraping / outbound crawling in the backend | `static scan of backend/*.py for HTTP clients and scrapers` | no requests/urllib/httpx/selenium/BeautifulSoup/scrapy usage | offenders=[] | **PASS** |
| SEC-17 | No account-enumeration endpoints | `inspect all API routes` | no lookup/enumeration style endpoints exist | routes=20, suspicious=[] | **PASS** |
| SEC-18 | Children's personal data is never requested or accepted | `3 child-related questions + child_name payload` | questions ask visibility only; child_name rejected with 422 | offenders=[], api=422 | **PASS** |
| SEC-19 | Vision helper performs face COUNT only | `static inspection of backend/services/vision_check.py` | detectMultiScale present, no recognition/identification APIs | count=True, offenders=[] | **PASS** |
| SEC-20 | Uploaded files are processed in memory, never stored | `POST /api/upload then inspect data/ directory` | HTTP 200 and no new files written | http=200, new_files=[] | **PASS** |
