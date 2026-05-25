@echo off
REM Elevate and run PowerShell installer
set SCRIPT=%~dp0ps_installer.ps1
powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process powershell -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File "%SCRIPT%"' -Verb RunAs"
