@echo off
title UNSTUCK - Public Online Launcher
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set "PATH=C:\Program Files\nodejs;%PATH%"

echo ========================================================
echo   UNSTUCK PLATFORM - PUBLIC ONLINE LAUNCHER
echo ========================================================
echo.

:: 1. Launch FastAPI Backend
echo [1/3] Starting Backend API (Port 8000)...
start "UNSTUCK Backend" cmd /k "cd /d ""%~dp0scraper (2)\scraper\mostaql_scraper"" && py -m uvicorn main:app --host 0.0.0.0 --port 8000"

:: 2. Launch Frontend dev server
echo [2/3] Starting Frontend Dev Server (Port 5173)...
start "UNSTUCK Frontend" cmd /k "cd /d ""%~dp0"" && npm run dev"

timeout /t 3 /nobreak >nul

:: 3. Launch Cloudflare Tunnel
echo [3/3] Launching Public Internet Tunnel...
echo.
echo ========================================================
echo   Your live public URL will appear below in seconds:
echo ========================================================
cloudflared.exe tunnel --url http://127.0.0.1:5173
pause
