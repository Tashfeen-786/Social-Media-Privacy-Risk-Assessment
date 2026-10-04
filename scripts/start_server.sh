#!/usr/bin/env bash
# One-command start: installs missing dependencies, then runs the app on :8000
set -e
cd "$(dirname "$0")/.."
python3 -c "import uvicorn, fastapi" 2>/dev/null || pip install --quiet -r requirements.txt
exec python3 -m uvicorn backend.app:app --host 0.0.0.0 --port 8000
