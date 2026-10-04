@echo off
REM Batch exposure-rubric assessment over the synthetic sample folders.
setlocal
cd /d "%~dp0.."
call .venv\Scripts\python.exe scripts\batch_assess.py
echo.
echo Summary written to reports\privacy_report.csv
pause
