# Privacy Risk Matrix

Likelihood × Impact, each rated LOW / MEDIUM / HIGH.

|  | **Impact LOW** | **Impact MEDIUM** | **Impact HIGH** |
|---|---|---|---|
| **Likelihood HIGH** | Public education details | Public phone number · Tag review disabled | MFA disabled · Password re-use |
| **Likelihood MEDIUM** | Handle re-used across platforms | Public e-mail · Old public posts not reviewed · Third-party apps not reviewed · Trackers on linked sites | Real-time location exposure · Unknown connections accepted · **Children/minors publicly visible** · Linked documents containing PII |
| **Likelihood LOW** | Public interests / hobbies | Public relationship status | Verification code (OTP) shared |

## Worked examples

| Risk | Likelihood | Impact | Rating | Reasoning |
|---|---|---|---|---|
| **Public phone number** | HIGH | MEDIUM | High | Automated collection of public numbers is common; leads to spam, smishing and recovery-flow abuse, but alone rarely causes account loss. |
| **Real-time location exposure** | MEDIUM | HIGH | High | Requires an interested observer, but discloses physical presence/absence with direct personal-safety consequences. |
| **MFA disabled** | HIGH | HIGH | Critical | Credential leaks are frequent and a single password then grants full account control. |
| **Third-party apps not reviewed** | MEDIUM | MEDIUM | Medium | Dormant integrations retain API access; impact depends on the scopes originally granted. |
| **Tag review disabled** | HIGH | MEDIUM | Medium-High | Tagging happens constantly; impact is reputational and adds to the public footprint. |
| **Children / minors in public media** | MEDIUM | HIGH | High | Requires an interested observer, but the subject cannot consent, the exposure persists for years and it can enable identification or unwanted contact. |
| **Linkage via link-in-bio / public documents** | MEDIUM | MEDIUM | Medium | Aggregators are easy to find; impact depends on what the linked documents contain (contact details, secrets). |
| **Third-party trackers on a linked site** | HIGH | LOW | Medium-Low | Extremely common; the privacy impact falls mostly on visitors rather than on the account itself. |

## Interpretation

Actual risk **depends on context** — who you are, how visible your role is, which platform,
which country, and what an adversary would gain. Two users with identical scores can face very
different real-world risk. Use this matrix as a prioritisation aid for awareness training,
not as a prediction of harm.
