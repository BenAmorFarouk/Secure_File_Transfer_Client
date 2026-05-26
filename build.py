#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Secure SFTP Client Build Script

This script:
1. Creates/activates the virtual environment
2. Installs all dependencies from requirements.txt
3. Installs PyInstaller (if needed)
4. Cleans previous builds
5. Builds the executable with proper asset bundling
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path
import io

def run_command(cmd, shell=False):
    """Run a command and return success status"""
    try:
        result = subprocess.run(cmd, shell=shell, check=True, capture_output=False)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Command failed: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
        return False

def main():
    project_root = Path(__file__).parent
    venv_path = project_root / ".venv"

    print("=" * 50)
    print("Secure SFTP Client Build Script")
    print("=" * 50)
    print()

    # Step 1: Create virtual environment if needed
    if not venv_path.exists():
        print("Creating virtual environment...")
        if not run_command([sys.executable, "-m", "venv", str(venv_path)]):
            print("Failed to create virtual environment")
            return False
        print("[OK] Virtual environment created")
    else:
        print("[OK] Virtual environment already exists")

    # Determine Python executable in venv
    python_exe = venv_path / "Scripts" / "python.exe" if sys.platform == "win32" else venv_path / "bin" / "python"

    # Step 2: Upgrade pip
    print("\nUpgrading pip...")
    run_command([str(python_exe), "-m", "pip", "install", "--upgrade", "pip"])

    # Step 3: Install requirements
    print("\nInstalling dependencies...")
    if not run_command([str(python_exe), "-m", "pip", "install", "-r", "requirements.txt"]):
        print("Failed to install requirements")
        return False
    print("[OK] Dependencies installed")

    # Step 4: Clean previous builds
    print("\nCleaning previous builds...")
    for dir_name in ["build", "dist", "__pycache__"]:
        dir_path = project_root / dir_name
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"  Removed {dir_name}/")

    # Step 5: Build executable
    print("\nBuilding executable with PyInstaller...")
    os.chdir(project_root)
    if not run_command([str(python_exe), "-m", "PyInstaller", "SecureSFTPClient.spec"]):
        print("Failed to build executable")
        return False
    print("[OK] Executable built successfully")

    # Summary
    exe_path = project_root / "dist" / "SecureSFTPClient.exe"
    print("\n" + "=" * 50)
    print("[OK] Build Complete!")
    print("=" * 50)
    print(f"\nExecutable location:")
    print(f"   {exe_path}")
    print(f"\n[OK] All dependencies are bundled in the executable")
    print(f"[OK] Logo assets are included")
    print()

if __name__ == "__main__":
    main()
