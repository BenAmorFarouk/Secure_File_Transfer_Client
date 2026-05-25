@echo off
REM Build Inno Setup installer (requires Inno Setup's ISCC.exe in PATH)
setlocal

echo Building Inno Setup installer...

if not exist "..\dist\SecureSFTPClient.exe" (
  echo ERROR: dist\SecureSFTPClient.exe not found. Build the project first.
  exit /b 1
)

where ISCC >nul 2>&1
if %errorlevel% neq 0 (
  echo ERROR: 'ISCC' (Inno Setup Compiler) not found. Install Inno Setup: https://jrsoftware.org/
  exit /b 2
)

cd /d %~dp0
ISCC SecureSFTPClient_installer.iss
if %errorlevel% neq 0 (
  echo Inno Setup build failed.
  exit /b %errorlevel%
)

echo Installer created: Output\SecureSFTPClient_Installer.exe
endlocal
