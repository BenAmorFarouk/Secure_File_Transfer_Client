# Secure File Transfer Client

A secure GUI SFTP client for Windows with local and remote file browsing, file upload/download, and text preview capabilities.

## ✨ Features

- 🗂️ Browse local filesystem directories and files
- 🔒 Secure SFTP server connections
- 📂 Browse remote folders and files  
- 📤📥 Upload and download files
- 👁️ Preview text files (local and remote)
- 🔑 Host key verification using `known_hosts`

## 🚀 Quick Start

### Run the Application

```bash
python run.py
```

### Build Standalone Executable

```bash
python build.py
```

The executable will be at: `dist/SecureSFTPClient.exe`

No Python installation needed on target machines!

## 📋 Requirements

- Python 3.10+
- Dependencies: See `requirements.txt`

Install with:

```bash
pip install -r requirements.txt
```

## 🏗️ Project Structure

Key files:
- `run.py` — Application entry point
- `main_enhanced.py` — Core application logic with GUI
- `local_fs.py` — Local file system operations
- `remote_sftp.py` — SFTP connection and remote file operations
- `utils.py` — Utility helper functions
- `build.py` — Build script for creating standalone executable
- `SecureSFTPClient.spec` — PyInstaller configuration

## 📦 Building & Distribution

### For Development
```bash
python run.py
```

### For End Users
1. Run: `python build.py`
2. Share: `dist/SecureSFTPClient.exe`
3. Users can run the .exe directly (no Python needed)

### GitHub Repository Contents
Commit source code, scripts, assets, and documentation only.
Do not commit generated or build-output files:
- `dist/`, `build/`
- `.venv/`, `env/`, `__pycache__/`, `*.pyc`
- `installer/*.exe`, `installer_inno/*.exe`
- `SecureSFTPClient.exe`, `logo.ico`
- `.vscode/` and other editor-specific folders

Built installers and executables should be published as GitHub release assets instead of stored in the repository.

- Use SSH key authentication when possible for better security.
- Host keys are verified and stored in `~/.ssh/known_hosts`; unknown hosts require explicit SHA256 fingerprint confirmation before trust is added.
- The client restricts weak SSH ciphers, MACs, key exchange algorithms, and legacy `ssh-rsa` pubkey algorithms for stronger transport security.
- Upload/download transfer integrity is verified with size checks and SHA-256 where feasible.
- The app saves host keys in `~/.ssh/known_hosts` and enforces secure permissions when supported by the OS.
- Large files are not previewed to avoid UI freezes.

## File structure

- `logo.png` – project logo for the repository and reference
- `logo.ico` – Windows icon generated from `logo.png` for the executable
- `run.py` – launcher script that starts the application
- `main_enhanced.py` – main application logic, GUI layout, and event handling
- `local_fs.py` – local filesystem browsing and file preview
- `remote_sftp.py` – secure SFTP connection and remote file operations
- `utils.py` – helper functions
- `build.py` – build script for creating standalone executable
- `SecureSFTPClient.spec` – PyInstaller configuration for building the executable
