@echo off
REM Runs all automated tests and regenerates docs\TEST_RESULTS.md
setlocal
cd /d "%~dp0.."
call .venv\Scripts\python.exe -m pytest tests -v
echo.
echo Test matrix written to docs\TEST_RESULTS.md
pause
