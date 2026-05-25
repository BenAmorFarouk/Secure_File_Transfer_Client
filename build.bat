@echo off
REM Secure SFTP Client Build Script
REM This script prepares the environment and builds the executable

echo ====================================
echo Secure SFTP Client Build Script
echo ====================================
echo.

REM Check if venv exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install/upgrade requirements
echo Installing Python dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

REM Clean previous builds
echo Cleaning previous builds...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "*.spec.bak" del *.spec.bak

REM Build the executable
echo Building executable with PyInstaller...
pyinstaller SecureSFTPClient.spec

echo.
echo ====================================
echo Build Complete!
echo ====================================
echo.
echo Executable location: dist\SecureSFTPClient.exe
echo.
pause
