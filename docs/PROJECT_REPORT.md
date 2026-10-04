# Project Report
## Social Media Privacy Risk Assessment Framework

*A defensive cybersecurity and privacy-engineering project. Version 2.0.*

---

### Abstract

Social-media users routinely underestimate how much of their identity, location and social graph
is publicly visible, and how that exposure interacts with weak account-security practices. This
project presents the **Social Media Privacy Risk Assessment Framework**, a defensive,
privacy-preserving system that measures social-media privacy exposure from **self-reported**
answers only — it never scrapes, tracks or profiles real users. A 58-question questionnaire across
ten categories is converted into structured numeric features, ten 0–100 category scores and a
single weighted 0–100 risk score (higher = higher assessed exposure) classified as LOW, MODERATE,
HIGH or CRITICAL. A second, complementary model — an eight-dimension **privacy exposure rubric**
(PII 25, geolocation/EXIF 20, children/minors 15, workplace/school 10, weak settings 10, linkage
10, handle correlation 5, trackers 5; final score = min(100, sum)) — runs on the same answers and
can additionally analyse a voluntarily supplied synthetic profile/posts export. The framework generates severity-rated findings, prioritised personalised
recommendations, an improvement simulator, a dashboard, and an exportable HTML/PDF report. It is
engineered Privacy-by-Design: no personal data is collected, and the database stores only
assessment identifiers, scores, finding types and timestamps — a claim verified by automated tests
that scan the raw database file and generated reports. A synthetic dataset of 1,200 fictional
records supports aggregate analytics. 51 automated tests were executed and all pass.

### 1. Introduction

Privacy on social platforms is configuration-driven: dozens of separate settings, spread across
menus, whose defaults drift towards greater visibility over time. Users receive plenty of generic
advice ("check your privacy settings") but very little that is specific, measurable and
prioritised. Meanwhile, the security consequences of oversharing — impersonation, phishing,
pretexting and account takeover — are usually taught separately from privacy settings. This
project joins the two: it treats privacy configuration and account-security controls as a single
measurable risk surface, and produces an explainable score plus a concrete remediation order.

### 2. Problem Statement

Existing approaches fall into two groups. Profile scanners inspect real profiles, which requires
scraping or platform access, raises serious ethical and legal issues, and cannot see
friends-only settings anyway. Static checklists are safe but generic: they cannot tell a user
*how exposed they are*, *which item matters most*, or *how much improvement a given change buys*.
There is no widely available, ethically clean, explainable instrument that quantifies personal
social-media privacy exposure from information the user already knows about their own settings.

### 3. Objectives

1. Quantify social-media privacy exposure on a 0–100 scale without any intrusive data collection.
2. Decompose that score into ten interpretable category scores with configurable weights.
3. Generate severity-rated findings with explanations and recommended actions.
4. Prioritise remediation as IMMEDIATE / IMPORTANT / GOOD PRACTICE.
5. Simulate the effect of selected improvements on the score.
6. Demonstrate Privacy-by-Design in an executable system, verified by tests.
7. Provide awareness material on digital footprint and social engineering, strictly defensive.

### 4. Social Media Privacy Background

Platform privacy models are audience-based: each attribute and each post has an audience
(public, connections, custom, private). Risk arises from three properties of these models:
(a) *defaults* are permissive and change over platform generations; (b) *granularity* is high,
so users rarely review every field; and (c) *persistence* — content published years ago remains
public unless explicitly limited. Contact attributes (phone, e-mail), identity attributes (full
birth date), affiliation attributes (employer, college) and spatio-temporal attributes (check-ins,
travel) carry disproportionate risk because they are re-used in identity verification and in
pretexting.

### 5. Digital Footprint

The digital footprint is the union of everything discoverable about a person online: active
profiles, search-engine-indexed pages, tagged content, abandoned accounts and re-used handles.
Two properties make it distinct from current privacy settings. First, **persistence** — a
well-configured account today does not retract an abandoned public account from 2016. Second,
**correlation** — a unique handle re-used across platforms links otherwise separate identities
into a single profile. The framework therefore scores footprint separately (self-search history,
abandoned public accounts, privacy-settings review cadence, handle re-use).

### 6. Privacy vs Security

Privacy answers *who can see what*; security answers *who can get in*. The framework scores both
because the failure modes compose: public contact details and affiliations raise the probability
of a targeted phishing or pretexting attempt, while missing MFA, re-used passwords and unreviewed
sessions determine whether that attempt succeeds. Account Security is therefore weighted equally
with Personal Information and Location Privacy at 15%.

### 7. Social Engineering

Social engineering exploits context rather than code. Publicly available employer, education,
travel, family and interest information allows an approach to appear pre-verified, which
suppresses the recipient's verification instinct. The framework measures behavioural exposure
(clicking unexpected links, confidence in recognising phishing, prior OTP sharing, engagement
with urgency/prize messages, out-of-band verification habits) and teaches conceptual defences.
**No attack content, templates or personalised pretexts are produced anywhere in this project.**

### 8. Existing Approaches

| Approach | Strengths | Weaknesses |
|---|---|---|
| Platform privacy check-ups | Authoritative, in-context | Per-platform, no score, no prioritisation, no security view |
| Profile scanners / scrapers | Observe actual public data | Ethically and legally problematic; blind to non-public settings |
| Static checklists (e.g. awareness posters) | Safe, simple, portable | Generic, unmeasured, no personalisation |
| Breach-exposure services | Concrete incident data | Only covers leaked credentials, not privacy configuration |
| **This framework** | Explainable score, ten categories, prioritised actions, simulation, zero data collection | Self-reported answers are unverified; weights are assumptions |

### 9. Proposed Framework

A four-stage pipeline: **collect → featurise → score → advise**. Collection is a validated
questionnaire that refuses sensitive fields. Featurisation maps every answer to a documented risk
value in [0,1] and derives control flags. Scoring produces category scores and a weighted overall
score with a full contribution breakdown. Advice comprises findings, recommendations, a checklist,
a report and an improvement simulation. Every stage is deterministic and inspectable.

### 10. Architecture

```
User → Questionnaire → Input Validation → Feature Extraction
     → {Profile, Personal Info, Location, Content, Account Security,
        Social Engineering, Digital Footprint} analyzers
     → Category Scores → Risk Scoring Engine → Overall Risk
     → Findings Engine → Recommendation Engine
     → Privacy Dashboard → Privacy Report → Anonymised Aggregates → Analytics DB
```

Implementation: FastAPI (routes, validation, security middleware), a services layer
(`scoring_engine`, `findings_engine`, `recommendation_engine`, `improvement_simulator`,
`report_generator`, `privacy_checklist`, `metadata_module`), a models layer (`questions`,
`categories`, `database`) and a static frontend with a vendored Chart.js. Diagram:
`screenshots/02_architecture.png`.

### 11. Questionnaire Design

58 questions in ten sections (CATEGORY A–J). Design rules: (1) never request a value, only a visibility or
behaviour; (2) offer a `NOT SURE` option and score it as elevated risk (0.7–0.8) because unknown
configuration is itself exposure; (3) mix protective questions (where YES is safe) with risky
questions (where YES is risky) to reduce acquiescence bias; (4) give each question an intra-category
weight reflecting its consequence — MFA 2.0, phone visibility 1.5, tag review 1.5, education 0.9.
Answer scales: visibility (PUBLIC/FRIENDS/PRIVATE/NOT SURE), yes-no (YES/SOMETIMES/NO/NOT SURE),
review cadence (REGULARLY/RARELY/NEVER/NOT SURE) and frequency (NEVER/RARELY/SOMETIMES/OFTEN).

### 12. Synthetic Dataset

`data/generate_dataset.py` produces `data/social_media_privacy_assessments.csv` with 1,200
fictional records (seeded, reproducible). Three behavioural personas — privacy-conscious (30%),
average (42%) and oversharer (28%) — bias the answer distribution; each synthetic response set is
scored by the *real* engine, so the dataset is internally consistent with the framework. Columns
cover profile/phone/email/birthday/location visibility, workplace, education, relationship, posts,
location tagging, travel posts, unknown connections, tag review, third-party app review, MFA,
login alerts, password reuse, suspicious-link awareness, old-post review, privacy-settings review,
ten category scores, the risk score and the risk level. Observed distribution: LOW 367,
MODERATE 176, HIGH 326, CRITICAL 331; mean score 43.9. **No real person's data is used.**

### 12a. The 20 Privacy Areas

The specification enumerates twenty privacy areas that must be assessed: profile visibility;
personal-information exposure; contact-information exposure; location exposure;
workplace/education exposure; birthday exposure; family/relationship information; post
visibility; friend/follower controls; tagging permissions; third-party application access;
account authentication; MFA usage; password-reuse awareness; login alerts; unknown connection
requests; suspicious links/messages; photo-metadata awareness; historical posts; and
social-engineering exposure. Every area is mapped to at least one questionnaire item through the
`area` field on each question, and `GET /api/privacy-areas` publishes the live coverage map.
Test **TC-44** fails the build if any area loses coverage.

### 12b. The 8-Category Exposure Rubric (Model B)

Alongside the behaviour-oriented ten-category model, the framework implements the exposure
rubric defined in the project specification:

| # | Exposure dimension | Max points |
|---|---|---|
| 1 | PII exposure (phone / e-mail / DOB / home information) | 25 |
| 2 | Geolocation / EXIF leakage and routine trails | 20 |
| 3 | Children / minors in media | 15 |
| 4 | Workplace / school disclosures (badges, room numbers) | 10 |
| 5 | Weak privacy settings (public account, open DMs, activity status) | 10 |
| 6 | Linkage risks (link-in-bio, public documents, repositories) | 10 |
| 7 | Reuse / handle correlation | 5 |
| 8 | Third-party trackers in linked sites | 5 |

Contributions are summed per dimension, capped at the dimension maximum, and the final score is
`min(100, Σ capped_points)`. Two entry points exist: `calculate_exposure_rubric(answers)` maps
questionnaire answers onto the rubric, while `score_profile(profile, posts)` is a rule-based
engine (regex for e-mail/phone, geo and EXIF flags, child flags, workplace keyword lists,
privacy-setting booleans, link inspection, handle comparison and declared tracker scripts) that
analyses a voluntarily supplied **synthetic** export. Caps are enforced and verified by
tests TC-36 and TC-39…TC-41.

### 12c. Relationship Between the Two Models

The two models are **complementary, not equivalent**, and the project never claims otherwise.
Model A is a weighted mean over behaviour and configuration questions; Model B is a capped
additive inventory of specific exposure dimensions. For the demonstration profile, Model A
returns 84.48 (CRITICAL) while Model B returns 93.30 (CRITICAL) — different numbers produced by
different mathematics from identical input. Read together they answer two different questions:
*"how good are my habits?"* and *"what is exposed right now?"*. Both are educational.
`docs/METHODOLOGY.md` documents the full derivation.

### 12d. Children and Minors

Minors cannot consent to their own exposure, and content about them persists for years, so the
rubric gives the dimension a dedicated 15-point allocation and the questionnaire adds three
items (child media visibility, child-related post visibility, school information involving
minors). Critically, the framework asks **only about visibility** — it never requests a child's
name, school, address or any other identifying detail, and the optional OpenCV helper counts
faces without recognition or age inference. Tests SEC-18 and SEC-19 enforce both rules.

### 12e. Linkage, Handle Correlation and Trackers

Three smaller dimensions capture correlation risk. *Linkage* covers link-in-bio aggregators and
publicly linked documents or repositories that may contain contact details or secrets. *Handle
correlation* captures the re-use of one username across platforms, which joins otherwise separate
identities into a single profile. *Trackers* is a deliberately basic, declaration-based
educational check on sites linked from the profile: it reads only what the supplied synthetic
file declares and never crawls, contacts or fingerprints anything.

### 13. Feature Engineering

`extract_privacy_features()` returns `question_risk` (per-question risk 0–1), `category_raw`
(weighted mean risk per category), `flags` (boolean finding triggers), `security_controls`
(eight named controls), and `exposure_counts` (public answers, not-sure answers, risky flags,
controls enabled). Examples of the mapping: public phone → personal-information exposure
contribution; public location → location-risk contribution; MFA disabled → account-security
contribution; unknown connections accepted → social-engineering/connection contribution; tag
review disabled → tagging contribution; third-party apps never reviewed → application-access
contribution.

### 14. Category Risk Analysis

Each category is scored independently so that a user with strong account security but heavy
oversharing is diagnosed correctly rather than averaged into a bland middle. Category score =
Σ(risk × weight) / Σ(weight) × 100. The ten categories are Profile Exposure, Personal Information,
Location Exposure, Content Exposure, Connection Risk, Tagging Risk, Account Security, Third-Party
App Risk, Social Engineering and Digital Footprint.

### 15. Risk Scoring

Overall = Σ(category score × category weight), with weights 10/15/15/10/10/5/15/5/10/5 percent.
Weights may be overridden per request or via `PRIVACY_WEIGHTS_FILE`; they are always renormalised
to 1.0 so the default configuration cannot be silently broken. Levels: LOW ≤20, MODERATE ≤40,
HIGH ≤70, CRITICAL >70. The API returns `score_breakdown` (per-category weight and contribution)
and `top_contributors` (ten highest-weighted answers), guaranteeing explainability.

### 16. Findings Engine

A catalogue of 50+ finding types maps flags to {category, severity, finding, explanation,
recommended action}. Severities are CRITICAL, HIGH, MEDIUM, LOW; findings are returned sorted by
severity. Examples: public phone number (CRITICAL), real-time location sharing (CRITICAL), MFA
disabled (CRITICAL), password re-use (CRITICAL), travel plans public (HIGH), tag review disabled
(HIGH), third-party apps not reviewed (HIGH), old public posts not reviewed (MEDIUM).

### 17. Recommendation Engine

Findings map deterministically to recommendations with priorities IMMEDIATE, IMPORTANT and GOOD
PRACTICE, plus two baseline hygiene recommendations. Output is sorted by priority so the user
always sees the highest-leverage action first. For the demo profile the engine returns 48
recommendations, 11 of them IMMEDIATE.

### 18. Improvement Simulator

Fifteen improvement bundles (make phone private, make birthday private, make location private,
disable real-time location sharing, make travel plans private, reject/verify unknown requests,
enable tag review, enable MFA, enable login alerts, fix password re-use, review third-party apps,
review old posts, review privacy settings, improve phishing awareness, make e-mail private) each
map to specific answer changes. The simulator re-scores the modified answer set and returns
current score/level, changes applied (with from→to per question), new score/level, absolute and
percentage risk reduction, and the change in finding count. Executed result for the demonstration
profile: **85.56 (CRITICAL) → 44.40 (HIGH), −41.16 points (−48.1%), findings 46 → 26.** The output
is explicitly labelled **FRAMEWORK SIMULATION** and does not claim real-world safety.

### 19. Account Security

Six questions cover MFA, login alerts, password re-use, session/device review, recovery
configuration and password-manager usage; two further controls (tag review, app review) are
tracked in the control inventory, giving the "Security Controls Enabled: n/8" dashboard card. MFA
carries the highest single-question weight in the framework.

### 20. Third-Party Applications

Four questions assess review cadence, breadth of social-login usage, removal of unused
integrations and scope-checking before authorisation. The category models least-privilege failure:
dormant integrations retain API access and inherit any breach of the vendor.

### 21. Location Privacy

Six questions cover home-city visibility, real-time check-ins, travel announcements, automatic
photo geotagging, home-identifying photos and live-location sharing. Real-time and predictive
disclosures are weighted above static ones because they reveal presence and absence rather than
just locale. The optional EXIF module reinforces the lesson by showing metadata actually embedded
in a photo the user voluntarily selects, processed entirely locally.

### 22. Digital Footprint Analysis

Four questions (self-search, abandoned public accounts, privacy-settings review cadence, handle
re-use) capture persistence and correlation risk. Although weighted at only 5%, this category
frequently produces the most surprising findings for users, because it concerns exposure they
have literally forgotten about.

### 23. Privacy Dashboard

Five top cards (Overall Risk Score, Risk Level, High-Risk Categories, Recommendations, Security
Controls Enabled) and six charts: category risk scores, privacy risk distribution, top privacy
weaknesses, account security controls, digital footprint risk and privacy improvement comparison.
The assessment view adds a radar chart, a weighting/contribution table, a findings table and a
recommendations table, plus the simulator with a before/after comparison chart. The interface is
responsive, uses a consistent dark cybersecurity design system, and has explicit loading and error
states.

### 24. Privacy by Design

All eight principles are implemented and mapped to code in `docs/PRIVACY_BY_DESIGN.md`: data
minimisation (schema + forbidden-field validator), purpose limitation, least privilege
(environment-based admin key), privacy by default (no accounts/cookies/trackers/CDN), transparency
(weights and contributions exposed), user control (delete endpoint), retention limitation and
secure processing (validation, escaping, headers, rate limiting, report guard).

### 25. Testing

76 automated tests were executed with pytest. The functional suite (TC-01…TC-36) covers the
required scenarios: fully private profile, fully public profile, each individual risk driver
(public phone, e-mail, birthday, location, real-time check-ins, travel plans, workplace,
education, public posts, unknown connections, tag review disabled, MFA disabled, login alerts
disabled, password re-use, apps not reviewed, low link awareness, old posts not reviewed, privacy
settings not reviewed), category and overall score calculation, the 20/40/70 boundaries,
recommendation generation, improvement simulation, database save, non-storage of sensitive data
and report generation; plus determinism, weight configurability, minimum coverage, questionnaire
size and finding-structure completeness. A pytest fixture records Test ID, scenario, input,
expected result, actual result and pass/fail, and writes `docs/TEST_RESULTS.md` at session end,
so the matrix is produced by the run itself.

### 26. Security Testing

The security suite (SEC-01…SEC-20) verifies security headers, input validation, rejection of
sensitive fields, non-reflection of XSS payloads, output escaping, rate limiting (70 requests →
exactly 60 allowed), the authorisation key concept, identifier validation against traversal and
SQL-injection strings, absence of sensitive data in the raw database file, non-persistence of raw
answers, safe report generation, data deletion, secrets-via-environment handling, transparency of
the privacy notice, minimality of returned stored fields, the absence of any scraping/HTTP-client code, the absence
of account-enumeration endpoints, that children's personal data is never requested or accepted,
that the vision helper is count-only, and that uploaded files are never written to disk. Two tests failed on first execution
(an ISO timestamp matched a naive phone regex, and the *finding type* string `password_reuse`
matched a password check); the detectors were corrected rather than the assertions weakened.

### 27. Results

| Scenario | Model A | Level | Model B | Findings |
|---|---|---|---|---|
| Fully private synthetic profile | 0.00 | LOW | 0.00 | 0 |
| Demonstration profile (synthetic) | 84.48 | CRITICAL | 93.30 | 51 |
| After the 9 specification improvements | 56.72 | HIGH | 71.80 | 39 |
| After all 20 improvements | 28.11 | MODERATE | 22.00 | 19 |
| Fully public synthetic profile | 100.00 | CRITICAL | 100.00 | 58 |
| Synthetic population (n=1,200) mean | 44.54 | — | 52.30 | — |
| Rule engine — synthetic `demo_oversharer` | — | CRITICAL | 100.00 | 26 |
| Rule engine — synthetic `demo_hardened` | — | LOW | 0.00 | 0 |

Population distribution (Model A): LOW 345, MODERATE 175, HIGH 345, CRITICAL 335.
Test execution: **76/76 passing**.

### 28. Limitations

Answers are self-reported and unverified, so a user who misremembers a setting receives an
inaccurate score. Weights and thresholds are reasoned assumptions, not empirically calibrated
values, and have not been validated against incident data. Platform feature parity is assumed;
some controls (e.g. tag review) do not exist everywhere. The simulator models the framework's own
re-score, not real-world attack probability. The synthetic dataset reflects designed personas,
not observed behaviour, so aggregate analytics are illustrative only.

### 29. Future Scope

Per-platform question profiles; expert-elicited or survey-calibrated weights; optional encrypted
accounts with expiry for longitudinal self-tracking; comparison against anonymised peer cohorts;
localisation and a WCAG AA accessibility audit; an offline desktop build; and a classroom mode
that aggregates anonymous class results for teaching.

### 30. Conclusion

The Social Media Privacy Risk Assessment Framework demonstrates that a useful, personalised
privacy-risk assessment can be built **without collecting any personal data at all**. By scoring
visibility and behaviour rather than values, keeping the model deterministic and explainable, and
proving the privacy claims with executed tests rather than assertions in documentation, the
project delivers both a working awareness tool and a concrete demonstration of Privacy-by-Design
engineering. The score is explicitly educational: it prioritises attention, it does not predict
compromise.

---

*Ethical statement: this project is designed for defensive cybersecurity and privacy education.
It uses synthetic or voluntarily provided assessment responses and does not scrape, track, or
profile real social-media users.*
