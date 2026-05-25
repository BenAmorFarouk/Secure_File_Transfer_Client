@echo off
REM Build installer using NSIS (makensis must be installed)
setlocal

echo Building NSIS installer...
if not exist "..\dist\SecureSFTPClient.exe" (
  echo ERROR: dist\SecureSFTPClient.exe not found. Build the project first.
  exit /b 1
)

where makensis >nul 2>&1
if %errorlevel% neq 0 (
  echo ERROR: 'makensis' not found. Install NSIS from https://nsis.sourceforge.io/Download
  exit /b 2
)

cd /d %~dp0
makensis SecureSFTPClient_installer.nsi
if %errorlevel% neq 0 (
  echo NSIS build failed.
  exit /b %errorlevel%
)

echo Installer created: SecureSFTPClient_Installer.exe
endlocal
