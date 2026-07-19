@echo off
REM Start the Atlas backend dev server.
REM Usage: run.bat  (from the smarttrack-backend folder)
cd /d "%~dp0"

REM Prefer the project venv if it exists, otherwise fall back to global python
if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
) else (
    python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
)
