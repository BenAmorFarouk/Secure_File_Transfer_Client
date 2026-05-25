# PROJECT STRUCTURE

## Directory Layout

```
Secure_File_Transfer_Client/
│
├── 📄 Source Code (Core Application)
│   ├── run.py                      Entry point - run this to start the app
│   ├── main.py                     Main application logic
│   ├── gui.py                      GUI components and UI layout
│   ├── local_fs.py                 Local filesystem operations
│   ├── remote_sftp.py              SFTP server connections
│   └── utils.py                    Utility functions
│
├── 🎨 Assets
│   ├── high-resolution-color-logo.png    Application logo (high-res)
│   └── logo.ico                          Windows executable icon
│
├── ⚙️ Build & Configuration
│   ├── build.py                    Automated build script (Python)
│   ├── build.bat                   Windows batch build script
│   ├── SecureSFTPClient.spec       PyInstaller configuration
│   ├── requirements.txt            Python dependencies
│   └── .gitignore                  Git ignore file
│
├── 📚 Documentation
│   ├── docs/
│   │   ├── BUILD.md                Build instructions
│   │   ├── ARCHITECTURE.md         Project architecture overview
│   │   └── DEVELOPMENT.md          Development guidelines
│   ├── README.md                   Main project readme
│
├── 🔧 Development & Environment
│   ├── .venv/                      Python virtual environment
│   ├── .vscode/                    VS Code settings
│   └── .git/                       Version control
│
└── 📦 Build Output (Auto-Generated)
    ├── build/                      PyInstaller build artifacts (temporary)
    └── dist/                       Final executable
        ├── SecureSFTPClient.exe    ⭐ Standalone application
        └── SecureSFTPClient/       Supporting files
```

## File Descriptions

### Source Code
| File | Purpose |
|------|---------|
| `run.py` | Application entry point |
| `main.py` | Core application class and event handling |
| `gui.py` | GUI layout, buttons, and UI components |
| `local_fs.py` | Local filesystem browsing functions |
| `remote_sftp.py` | SFTP connection and remote operations |
| `utils.py` | Helper functions and utilities |

### Configuration & Build
| File | Purpose |
|------|---------|
| `requirements.txt` | Python package dependencies |
| `SecureSFTPClient.spec` | PyInstaller build configuration |
| `build.py` | Automated build script (recommended) |
| `build.bat` | Windows batch build alternative |

### Documentation
| File | Purpose |
|------|---------|
| `README.md` | Project overview and getting started |
| `docs/BUILD.md` | Detailed build instructions |
| `docs/ARCHITECTURE.md` | Technical architecture and design |
| `docs/DEVELOPMENT.md` | Development guidelines |

## Key Directories

### `.venv/`
Python virtual environment with all installed packages.
**Keep:** Yes - needed for development

### `build/`
Temporary PyInstaller build artifacts.
**Keep:** No - auto-generated, safe to delete

### `dist/`
Final compiled executables.
**Keep:** Yes - contains your application

### `.git/`
Git version control repository.
**Keep:** Yes - preserves project history

## Development Workflow

1. **Edit code** → Modify `.py` files
2. **Test** → `python run.py`
3. **Build** → `python build.py`
4. **Distribute** → Share `dist/SecureSFTPClient.exe`

## Cleanup Notes

- `build/` folder is auto-generated and can be safely deleted
- `dist/` contains your executable - keep safe
- `.venv/` folder is large but necessary for development
- All `.py` source files are essential
- Documentation in `docs/` is for reference
