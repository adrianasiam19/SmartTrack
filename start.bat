@echo off
REM ================================================================
REM  start.bat — Launch both Atlas backend (FastAPI) and frontend (Next.js)
REM
REM  Usage:
REM    start.bat              — Start backend then frontend
REM    start.bat backend      — Start backend only
REM    start.bat frontend     — Start frontend only
REM ================================================================
setlocal enabledelayedexpansion

set ROOT_DIR=%~dp0
set BACKEND_DIR=%ROOT_DIR%smarttrack-backend
set FRONTEND_DIR=%ROOT_DIR%smarttrack-frontend

:MENU
if /I "%1"=="backend" goto BACKEND
if /I "%1"=="frontend" goto FRONTEND
if /I "%1"=="" goto BOTH
echo Unknown argument: %1
echo Usage: start.bat [backend^|frontend]
exit /b 1

:BOTH
echo ============================================================
echo  Starting Atlas — Backend ^& Frontend
echo ============================================================
echo.

REM Start backend in a new window
start "Atlas Backend" cmd /c "cd /d "%BACKEND_DIR%" && echo [Backend] Starting FastAPI server... && python run.py"

REM Give the backend a moment to initialize
timeout /t 3 /nobreak >nul

REM Start frontend in a new window
start "Atlas Frontend" cmd /c "cd /d "%FRONTEND_DIR%" && echo [Frontend] Starting Next.js dev server... && npx next dev"

echo.
echo Both servers are starting up:
echo   Backend  → http://localhost:8000
echo   Frontend → http://localhost:3000
echo   API Docs → http://localhost:8000/docs
echo.
echo Close the terminal windows to stop the servers.
goto END

:BACKEND
echo Starting Atlas Backend...
cd /d "%BACKEND_DIR%"
echo   Port: 8000
echo   DB:  Neon PostgreSQL
python run.py
goto END

:FRONTEND
echo Starting Atlas Frontend...
cd /d "%FRONTEND_DIR%"
echo   Port: 3000
npx next dev
goto END

:END
endlocal
