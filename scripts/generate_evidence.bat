@echo off
REM ==========================================================================
REM  Regenerates all automatically generatable evidence into screenshots\
REM  Browser screenshots need BOTH servers running and Playwright installed.
REM ==========================================================================
setlocal
cd /d "%~dp0.."
echo [1/5] Demo assessment + privacy report...
call .venv\Scripts\python.exe scripts\run_demo_assessment.py

echo [2/5] Batch exposure assessment (synthetic samples)...
call .venv\Scripts\python.exe scripts\batch_assess.py

echo [3/5] Local evidence (structure, architecture, dataset, tests, schema, README)...
call .venv\Scripts\python.exe scripts\generate_local_evidence.py

echo [4/5] Installing Playwright browser (first run only)...
call .venv\Scripts\python.exe -m pip install playwright
call .venv\Scripts\python.exe -m playwright install chromium

echo [5/5] Browser screenshots (backend :8000 and frontend :5173 must be running)...
call .venv\Scripts\python.exe scripts\capture_screenshots.py

echo.
echo Evidence written to screenshots\  - see screenshots\README.md
pause
