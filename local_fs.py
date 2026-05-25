from pathlib import Path
from typing import List, Tuple
import os

class LocalFileSystem:
    MAX_PREVIEW_BYTES = 2 * 1024 * 1024

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
                if "/" in folder_name or "\\" in folder_name:
                    return False
                new_path = self.current_folder / folder_name

            if new_path.is_dir():
                self.current_folder = new_path.resolve()
                return True
        except Exception:
            pass
        return False

    def get_selected_file(self, filename: str) -> str:
        """Get the full path of a selected file"""
        try:
            filename = os.path.basename(filename.strip())
            if not filename:
                return None
            file_path = (self.current_folder / filename).resolve()
            if file_path.is_file() and file_path.parent == self.current_folder:
                return str(file_path)
        except Exception:
            pass
        return None

    def get_full_path(self) -> str:
        """Get the current folder path as string"""
        return str(self.current_folder)

    def read_file_content(self, filename: str) -> str:
        """Read the content of a file. Returns content or error message."""
        try:
            filename = os.path.basename(filename.strip())
            if not filename:
                return "Error: invalid filename"
            file_path = (self.current_folder / filename).resolve()
            if not file_path.is_file() or file_path.parent != self.current_folder:
                return f"Error: {filename} is not a file"

            size = file_path.stat().st_size
            if size > self.MAX_PREVIEW_BYTES:
                return f"File too large to preview ({size} bytes)."
            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                return content
            except Exception as e:
                return f"Error reading file: {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"