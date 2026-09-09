@echo off
cd /d "%~dp0backend"

if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else (
    echo Virtual env not found. Create it with: python -m venv .venv
    echo Then install deps: pip install -r requirements.txt
    pause
    exit /b 1
)

echo Starting backend at http://localhost:8000
.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
