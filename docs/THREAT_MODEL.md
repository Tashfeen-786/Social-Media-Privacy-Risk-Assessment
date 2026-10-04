# Defensive Threat Model — Fictional Social-Media User

**Subject:** "Alex Fictional", a synthetic demonstration user. No real person is modelled.
**Purpose:** defensive analysis only. This document contains **no** attack instructions,
tooling, payloads or social-engineering scripts.

## Assets

| ID | Asset | Why it matters |
|---|---|---|
| A1 | Account (credentials + session) | Controls identity and all content |
| A2 | Identity information (name, DOB, education) | Enables identity fraud and verification abuse |
| A3 | Contact information (phone, e-mail) | Entry point for phishing/smishing and recovery abuse |
| A4 | Location privacy (home city, check-ins, travel) | Physical safety and presence/absence signals |
| A5 | Private content (photos, stories, messages) | Reputation, blackmail and profiling exposure |
| A6 | Social relationships (friends, family, colleagues) | Trust graph exploited by impersonation |
| A7 | Children / minors appearing in media | Cannot consent; exposure is persistent and re-identifiable |
| A8 | Linked sites, documents and repositories | Secondary leak path for PII and secrets |

## Threat analysis

| # | Asset | Threat | Exposure (how it becomes possible) | Potential impact | Existing control | Recommended control |
|---|---|---|---|---|---|---|
| T1 | A1 | Account takeover | Re-used password + MFA disabled + no login alerts | Full loss of account, messages sent as the user | Platform password policy | Enable MFA, unique password in a manager, enable login alerts, review sessions |
| T2 | A2/A6 | Impersonation (profile cloning) | Public profile photo, public friend list, public bio | Contacts deceived by a cloned account | Platform reporting flow | Limit photo/friend-list visibility, enable profile-picture guard, periodic self-search |
| T3 | A3 | Phishing / smishing | Public e-mail and phone, open DMs from strangers | Credential theft, malware, financial loss | Spam filtering | Hide contact fields, restrict message requests, never open unexpected links |
| T4 | A1/A6 | Social engineering & pretexting | Public employer, college, travel plans, family links | Believable pretexts, OTP hand-over, fraud | User awareness (variable) | Reduce public detail, verify unusual requests out-of-band, never share verification codes |
| T5 | A2/A5 | Unwanted profiling / data aggregation | Search-engine indexing, handle re-use, abandoned public accounts | Long-term correlated profile across platforms | None by default | Disable search indexing, vary handles, close/secure unused accounts |
| T6 | A4/A5 | Oversharing (physical & reputational) | Real-time check-ins, travel posts, geotagged photos, documents | Home targeted while away, routine mapped | Occasional self-censorship | Post after leaving, disable geotagging, review old posts, limit audiences |
| T7 | A1/A5 | Third-party application exposure | Apps never reviewed, unused integrations, broad scopes | Silent API access to profile data, breach spillover | Platform app list | Review and revoke apps quarterly, check scopes before authorising |
| T8 | A7 | Exposure of minors | Public child media, child-related captions, school details | Identification of a child, unwanted contact, lasting footprint | Parental judgement (variable) | Restrict child media to private audiences, remove school/route identifiers, blur faces |
| T9 | A8 | Linkage / correlation | Link-in-bio aggregators, public docs and repos, re-used handle | One discovered identity unlocks all others; secrets leak from repos | None by default | Prune aggregator links, scan repos for .env/keys, use distinct handles |
| T10 | A2/A5 | Third-party tracking on linked sites | Analytics/ad scripts on a linked personal site, no privacy notice | Visitor profiling associated with your identity | None by default | Reduce third-party scripts, add a cookie/privacy notice, gate analytics behind consent |

## Residual risk

Even with all recommended controls applied, residual risk remains from platform-side breaches,
contacts re-sharing content, and information already published historically. The framework
therefore treats privacy as continuous maintenance, not a one-time fix.
