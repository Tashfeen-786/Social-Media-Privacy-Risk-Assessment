@echo off
REM Starts the FastAPI backend (also serves the static frontend).
setlocal
cd /d "%~dp0.."
echo Backend : http://127.0.0.1:8000
echo Swagger : http://127.0.0.1:8000/docs
echo (Ctrl+C to stop)
call .venv\Scripts\python.exe -m uvicorn backend.app:app --host 0.0.0.0 --port 8000
pause
