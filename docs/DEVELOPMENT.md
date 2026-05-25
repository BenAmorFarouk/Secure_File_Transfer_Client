# DEVELOPMENT GUIDE

## Development Setup

### 1. Clone or Enter Project
```powershell
cd C:\Study\Secure_File_Transfer_Client
```

### 2. Activate Virtual Environment
```powershell
.venv\Scripts\activate
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

## Running Locally

### Start the Application
```powershell
python run.py
```

The GUI will launch with a local file browser and SFTP connection form.

## Development Workflow

```
1. Make code changes
   ↓
2. Test: python run.py
   ↓
3. Verify functionality
   ↓
4. Build: python build.py
   ↓
5. Test executable: dist/SecureSFTPClient.exe
   ↓
6. Commit and push
```

## Code Organization

### gui.py
- `SFTPInterface` class - Main GUI layout
- Button callbacks and event handlers
- UI component creation and updates

### main.py
- `SFTPApp` class - Application controller
- Event binding and callbacks
- File operations coordination

### remote_sftp.py
- `RemoteSFTP` class - SFTP connection management
- Remote file operations (list, upload, download)
- SSH key handling

### local_fs.py
- `LocalFileSystem` class - Local file browsing
- Directory/file listing
- File operations (read, write, delete)

### utils.py
- Helper functions
- Common utilities

## Building for Distribution

### Create Executable
```powershell
python build.py
```

### Output Location
```
dist/SecureSFTPClient.exe  ← Ready to distribute
dist/SecureSFTPClient/     ← Supporting files (included in exe)
```

### Share with Users
- Send only: `dist/SecureSFTPClient.exe`
- No Python installation required on user's machine
- All dependencies are bundled

## Modifying Build Configuration

The build configuration is in `SecureSFTPClient.spec`:

```python
datas=[
    ('high-resolution-color-logo.png', '.'),
    ('logo.ico', '.'),
],
hiddenimports=[
    'customtkinter',
    'paramiko',
    'tkinter',
],
```

If you add new assets or dependencies:
1. Add new imports to `hiddenimports` if not auto-detected
2. Add new asset files to `datas`
3. Rebuild with `python build.py`

## Dependencies

See `requirements.txt` for all dependencies:

- **customtkinter** - Modern GUI framework
- **paramiko** - SFTP/SSH client
- **pyinstaller** - Executable builder

## Code Style

- Use clear, descriptive variable names
- Add comments for complex logic
- Keep functions focused and single-purpose
- Handle exceptions gracefully

## Testing Checklist

Before building for release:

- [ ] Test local file browsing
- [ ] Test SFTP connection
- [ ] Test file upload/download
- [ ] Test file preview feature
- [ ] Test host key verification
- [ ] No console errors or warnings

## Troubleshooting Development

### Module import errors
```powershell
# Ensure venv is activated and dependencies installed
.venv\Scripts\activate
pip install -r requirements.txt
```

### GUI not launching
```powershell
# Check for error messages
python run.py
# Look at terminal output for traceback
```

### Build fails
```powershell
# Clean and rebuild
python build.py
# If still fails, check build/SecureSFTPClient/warn-SecureSFTPClient.txt
```

## Git Workflow

```powershell
# View status
git status

# Stage changes
git add .

# Commit
git commit -m "Description of changes"

# Push
git push origin main
```

### .gitignore Includes
- `.venv/` - Virtual environment
- `build/` - PyInstaller artifacts
- `dist/` - Compiled executables (optional)
- `__pycache__/` - Python cache
- `*.pyc` - Compiled Python files

## Release Checklist

1. ✅ All tests pass
2. ✅ Code reviewed
3. ✅ Comments and docstrings updated
4. ✅ README.md accurate
5. ✅ Build with `python build.py`
6. ✅ Test `dist/SecureSFTPClient.exe`
7. ✅ Tag release in git
8. ✅ Share executable

## Questions?

Refer to:
- [README.md](../README.md) - Project overview
- [BUILD.md](BUILD.md) - Build instructions
- [ARCHITECTURE.md](ARCHITECTURE.md) - Project structure
