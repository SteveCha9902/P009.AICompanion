@echo off
title P009 AI Companion Launcher
echo ========================================================
echo [P009 AI Companion] Starting Backend and Mobile App...
echo ========================================================

start "P009_Backend_8000" cmd /k "%~dp0run_backend.bat"
ping 127.0.0.1 -n 3 > nul
start "P009_Mobile_8081" cmd /k "%~dp0run_mobile.bat"

echo.
echo Backend (port 8000) and Mobile Metro (port 8081) started in separate windows.
