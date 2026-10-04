@echo off
REM Demonstrates weight calibration against synthetic reference ratings.
setlocal
cd /d "%~dp0.."
call .venv\Scripts\python.exe scripts\calibrate.py --records 200
pause
