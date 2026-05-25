# BUILD INSTRUCTIONS

## Quick Build (Recommended)

```powershell
cd C:\Study\Secure_File_Transfer_Client
python build.py
```

Your executable will be at: `dist/SecureSFTPClient.exe`

## What the Build Does

The automated build script:
1. ✅ Creates/activates Python virtual environment
2. ✅ Installs all dependencies from requirements.txt
3. ✅ Cleans previous builds
4. ✅ Compiles with PyInstaller
5. ✅ Bundles all assets (high-resolution logo, dependencies, etc.)

**Result:** Standalone executable (~17 MB) with no external dependencies needed.

## Automated Build Scripts

### Option 1: Python Script (Cross-Platform)
```powershell
python build.py
```

### Option 2: Windows Batch Script
```cmd
build.bat
```

## Manual Build

If you prefer manual control:

```powershell
# Activate virtual environment
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Build executable
pyinstaller SecureSFTPClient.spec
```

## Build Configuration

The build uses `SecureSFTPClient.spec` which:
- Bundles all Python dependencies (customtkinter, paramiko, etc.)
- Includes high-resolution logo assets
- Sets application icon
- Creates windowed GUI application

## Output Structure

```
dist/
├── SecureSFTPClient.exe          ← Standalone executable
└── SecureSFTPClient/              ← Supporting files
    ├── high-resolution-color-logo.png
    └── [other dependencies]
```

## Distribution

For end users, just provide: `dist/SecureSFTPClient.exe`

Users can:
- Download the file
- Run directly (no Python needed)
- All dependencies included

## Troubleshooting

**Build fails:** Delete `build/` and `dist/` folders, then rebuild
**Missing modules:** Ensure all dependencies are in requirements.txt
**Icon not showing:** Verify `logo.ico` exists in project root
**Executable too large:** Normal for bundled Python apps with customtkinter

## Requirements Met

✅ PyInstaller installed and configured  
✅ All dependencies bundled in executable  
✅ High-resolution logo included  
✅ Automated build process  
✅ Clean, documented build system  
