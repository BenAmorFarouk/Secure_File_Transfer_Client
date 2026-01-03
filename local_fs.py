from pathlib import Path
from typing import List, Tuple
import os

class LocalFileSystem:
    def __init__(self):
        self.current_folder = Path.home()

    def get_folders(self) -> List[str]:
        folders = []
        try:
            if self.current_folder != self.current_folder.anchor:
                folders.append("..")
            for p in self.current_folder.iterdir():
                if p.is_dir() and not p.name.startswith('.'):
                    try:
                        if p.stat().st_mode & 0o400:
                            folders.append(p.name)
                    except (PermissionError, OSError):
                        continue
            folders.sort(key=str.lower)
        except (PermissionError, FileNotFoundError):
            pass
        return folders

    def get_files(self) -> List[Tuple[str, int]]:
        files = []
        try:
            for p in self.current_folder.iterdir():
                if p.is_file() and not p.name.startswith('.'):
                    try:
                        if p.stat().st_mode & 0o400:
                            size = p.stat().st_size
                            files.append((p.name, size))
                    except (PermissionError, OSError):
                        continue
            files.sort(key=lambda x: x[0].lower())
        except (PermissionError, FileNotFoundError):
            pass
        return files

    def navigate_to(self, folder_name: str) -> bool:
        try:
            folder_name = folder_name.strip()
            if folder_name == "..":
                new_path = self.current_folder.parent
                if new_path == self.current_folder:
                    return False
            else:
                new_path = self.current_folder / folder_name

            if new_path.is_dir():
                self.current_folder = new_path.resolve()
                return True
        except Exception:
            pass
        return False