# GitHub Setup Instructions

> **No repository, commit, URL or screenshot has been created or fabricated for you.**
> Evidence items 27 and 28 must be captured by you after you push.

## 1. Create the repository
On GitHub, create a **public** repository named:

```
Social-Media-Privacy-Risk-Assessment
```

Description:

```
Privacy-focused cybersecurity framework for assessing social-media exposure, account-security practices, social-engineering risk, digital-footprint risk, and personalized privacy improvements using synthetic/self-reported data.
```

Topics: `cybersecurity` `privacy` `privacy-by-design` `risk-assessment` `fastapi` `python`
`security-awareness` `social-engineering` `digital-footprint` `grc`

Do **not** initialise with a README (this project already has one).

## 2. Verify nothing sensitive is committed
```bash
git status --short
type .gitignore
dir /b .env            # must NOT exist; only .env.example is committed
```
`.gitignore` already excludes `.env`, `*.db`, generated reports, caches and virtual environments.

## 3. Push
```bash
cd Social-Media-Privacy-Risk-Assessment
git init
git add .
git commit -m "feat: social media privacy risk assessment framework (engine, API, dashboard, tests, docs)"
git branch -M main
git remote add origin https://github.com/<your-username>/Social-Media-Privacy-Risk-Assessment.git
git push -u origin main
```

### Suggested commit history (if you prefer multiple commits)
```bash
git add backend/ requirements.txt && git commit -m "feat(backend): scoring, findings, recommendation and simulation engines"
git add frontend/ && git commit -m "feat(frontend): questionnaire, results and privacy dashboard"
git add data/ && git commit -m "feat(data): synthetic dataset generator (1,200 fictional records)"
git add tests/ && git commit -m "test: 51 functional and security/privacy tests"
git add docs/ screenshots/ README.md && git commit -m "docs: report, threat model, risk matrix and evidence"
```

## 4. Capture the account-dependent evidence (MANUAL)
| Item | Filename | How |
|---|---|---|
| 27 | `screenshots/27_github_commits.png` | Repository → **Commits** tab → full-window screenshot |
| 28 | `screenshots/28_github_repository.png` | Repository home page showing README, description and topics |

Save both into `screenshots/` using exactly those filenames.
