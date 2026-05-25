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

## 📚 Documentation

- **[BUILD.md](docs/BUILD.md)** — Detailed build instructions
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** — Project structure and design
- **[DEVELOPMENT.md](docs/DEVELOPMENT.md)** — Development guidelines

## 🏗️ Project Structure

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for complete project layout.

Key files:
- `run.py` — Application entry point
- `main.py` — Core application logic
- `gui.py` — User interface
- `local_fs.py` — Local file operations
- `remote_sftp.py` — SFTP operations
- `utils.py` — Utility functions

## 📦 Building & Distribution

### For Development
```bash
python run.py
```

### For End Users
1. Run: `python build.py`
2. Share: `dist/SecureSFTPClient.exe`
3. Users can run the .exe directly (no Python needed)

See [BUILD.md](docs/BUILD.md) for details.

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
- The app saves host keys in `~/.ssh/known_hosts` and enforces secure permissions.
- Large files are not previewed to avoid UI freezes.

## File structure

- `logo.png` – project logo for the repository and reference
- `logo.ico` – Windows icon generated from `logo.png` for the executable
- `run.py` – launcher script that starts the GUI
- `main.py` – main application logic and event wiring
- `gui.py` – GUI layout and user interaction handlers
- `local_fs.py` – local filesystem browsing and file preview
- `remote_sftp.py` – secure SFTP connection and remote file operations
- `utils.py` – helper functions
