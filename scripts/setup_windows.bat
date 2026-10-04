@echo off
REM ==========================================================================
REM  Social Media Privacy Risk Assessment Framework - Windows setup
REM  Creates the Python virtual environment, installs every backend
REM  dependency, and installs the React (Vite) frontend dependencies.
REM ==========================================================================
setlocal
cd /d "%~dp0.."
echo.
echo [1/6] Checking Python...
python --version || (echo ERROR: Python 3.10+ is required and must be on PATH & pause & exit /b 1)

echo [2/6] Creating virtual environment (.venv)...
if not exist .venv (python -m venv .venv)

echo [3/6] Upgrading pip...
call .venv\Scripts\python.exe -m pip install --upgrade pip

echo [4/6] Installing backend requirements...
call .venv\Scripts\python.exe -m pip install -r requirements.txt

echo [5/6] Creating .env from .env.example (if missing)...
if not exist .env (copy .env.example .env >nul & echo     .env created)

echo [6/6] Installing React frontend dependencies (needs Node.js 18+)...
where node >nul 2>nul
if errorlevel 1 (
  echo     WARNING: Node.js not found. The React UI on :5173 will be unavailable.
  echo     The static frontend served by the backend on :8000 still works.
) else (
  pushd frontend-react
  call npm install
  popd
)

echo.
echo ==========================================================
echo  Setup complete.
echo    next:  scripts\generate_dataset.bat
echo           scripts\start_backend.bat    -^> http://127.0.0.1:8000
echo           scripts\start_frontend.bat   -^> http://localhost:5173
echo           Swagger                      -^> http://127.0.0.1:8000/docs
echo ==========================================================
pause
