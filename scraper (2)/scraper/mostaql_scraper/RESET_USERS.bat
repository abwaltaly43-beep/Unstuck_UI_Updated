@echo off
cd /d "%~dp0"
echo ========================================================
echo   UNSTUCK - Reset All Users and Auth Records
echo ========================================================
py reset_users.py
pause
