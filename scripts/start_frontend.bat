@echo off
REM ==========================================================================
REM  Starts the React + Vite frontend on http://localhost:5173
REM  It proxies /api to the backend on http://127.0.0.1:8000,
REM  so start_backend.bat must be running in another window.
REM ==========================================================================
setlocal
cd /d "%~dp0..\frontend-react"
where node >nul 2>nul
if errorlevel 1 (
  echo ERROR: Node.js 18+ is required for the React frontend.
  echo Alternative: the static frontend is served by the backend at http://127.0.0.1:8000
  pause & exit /b 1
)
if not exist node_modules (echo Installing dependencies... & call npm install)
echo Frontend: http://localhost:5173
start "" http://localhost:5173
call npm run dev
pause
