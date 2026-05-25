# Quick Access Guide

## 🚀 Running the Application

### Option 1: Desktop Shortcut (Easiest)
Double-click the **"Secure SFTP Client"** icon on your desktop to launch the application.

### Option 2: From Project Folder
```powershell
cd C:\Study\Secure_File_Transfer_Client
python run.py
```

### Option 3: From Built Executable
```powershell
C:\Study\Secure_File_Transfer_Client\dist\SecureSFTPClient.exe
```

---

## 🎨 Logo Configuration

Your project uses **two logos**:

### High-Resolution Logo
- **File:** `high-resolution-color-logo.png` (10 KB)
- **Usage:** Bundled in the executable
- **Purpose:** High-quality logo for the application UI
- **Location:** Automatically included in builds

### Desktop Icon
- **File:** `logo.ico` (7 KB)  
- **Usage:** Desktop shortcuts and window title bar
- **Purpose:** Application icon for Windows
- **Location:** Desktop shortcut uses this icon

---

## 📌 Desktop Shortcut Details

### Location
```
C:\Users\user\Desktop\Secure SFTP Client.lnk
```

### What It Does
- Points to the standalone executable
- Uses the logo.ico for the desktop icon
- Working directory set to project folder
- Windowed mode (GUI)

### To Recreate the Shortcut
If you accidentally delete it, run:
```powershell
cd C:\Study\Secure_File_Transfer_Client
python build.py   # Rebuild if needed
# Then create shortcut again using the script
```

---

## 🔄 Build & Deploy

### Build New Executable
```powershell
python build.py
```

Both logos are **automatically bundled** in the new executable.

### Update Desktop Shortcut
The shortcut always points to the latest executable in `dist/`.

---

## ✅ Verified Setup

- ✓ High-resolution logo configured
- ✓ Desktop icon configured  
- ✓ Desktop shortcut created and ready
- ✓ All logos bundled in executable
- ✓ Application ready to use

Just double-click the desktop shortcut to launch! 🚀
