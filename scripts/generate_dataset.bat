@echo off
REM Generates the synthetic dataset (1,200 fictional records) and seeds the DB.
setlocal
cd /d "%~dp0.."
call .venv\Scripts\python.exe data\generate_dataset.py --records 1200 --seed 42
call .venv\Scripts\python.exe scripts\seed_database.py 300
echo.
echo Dataset : data\social_media_privacy_assessments.csv
echo Database: data\privacy_assessment.db
pause
