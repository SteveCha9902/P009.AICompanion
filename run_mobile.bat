@echo off
title P009 AI Companion Mobile
echo ========================================================
echo [P009 AI Companion] Starting Expo Metro Bundler...
echo ========================================================
cd /d "%~dp0mobile"
call npx expo start -c
pause
