@echo off
REM Build Installer Script for Secure SFTP Client using NSIS
REM This script builds the installer using NSIS (makensis)

setlocal enabledelayedexpansion

echo ==================================================
echo Secure SFTP Client Installer Builder (NSIS)
echo ==================================================
echo.

REM Get the project root
set "projectRoot=%~dp0"
set "nsiScript=%projectRoot%installer\SecureSFTPClient_installer.nsi"
set "distDir=%projectRoot%dist"
set "exePath=%distDir%\SecureSFTPClient.exe"

REM Check if executable exists
if not exist "%exePath%" (
    echo [ERROR] Executable not found at: %exePath%
    echo [INFO] Please run 'python build.py' first to build the executable
    exit /b 1
)

echo [OK] Executable found: %exePath%
echo.

REM Check for NSIS installation
set "nsisPath="
if exist "C:\Program Files (x86)\NSIS\Bin\makensis.exe" (
    set "nsisPath=C:\Program Files (x86)\NSIS\Bin\makensis.exe"
) else if exist "C:\Program Files\NSIS\Bin\makensis.exe" (
    set "nsisPath=C:\Program Files\NSIS\Bin\makensis.exe"
)

if "!nsisPath!"=="" (
    echo [ERROR] NSIS not found!
    echo.
    echo Please install NSIS from: https://nsis.sourceforge.io/
    echo.
    echo After installation, run this script again.
    exit /b 1
)

echo [OK] Found NSIS at: !nsisPath!
echo.

REM Build the installer
echo Building installer...
echo.

"!nsisPath!" "%nsiScript%"

if %ERRORLEVEL% equ 0 (
    echo.
    echo ==================================================
    echo [OK] Installer Built Successfully!
    echo ==================================================
    echo.

    set "installerPath=%distDir%\SecureSFTPClient_Installer.exe"
    if exist "!installerPath!" (
        for /F "usebackq" %%A in ('!installerPath!') do set "size=%%~zA"
        set /A sizeMB=!size! / 1048576
        echo Installer location:
        echo    !installerPath!
        echo.
        echo Installer size: !sizeMB! MB
        echo.
        echo [OK] Ready to share with your friends!
    )
) else (
    echo.
    echo [ERROR] Installer build failed!
    exit /b 1
)

endlocal
