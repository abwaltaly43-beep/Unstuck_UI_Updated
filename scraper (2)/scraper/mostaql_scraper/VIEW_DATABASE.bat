@echo off
title UNSTUCK - Database Viewer
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
echo ========================================================
echo   UNSTUCK - Visual Database Inspector
echo ========================================================
py view_database.py
if errorlevel 1 (
    python view_database.py
)
pause
