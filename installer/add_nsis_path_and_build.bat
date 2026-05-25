@echo off
setlocal EnableDelayedExpansion
set "P=%PATH%;C:\Program Files (x86)\NSIS\Bin"
setx PATH "!P!"
set "PATH=!P!"
cd /d "%~dp0"
build_installer.bat
