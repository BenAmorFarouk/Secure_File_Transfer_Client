import paramiko
from typing import List, Tuple, Optional

class RemoteSFTP:
    def __init__(self):
        self.ssh: Optional[paramiko.SSHClient] = None
        self.sftp: Optional[paramiko.SFTPClient] = None
        self.current_path = "/"

    def connect(self, host: str, port: int, username: str, password: str) -> bool:
        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(
                hostname=host,
                port=port,
                username=username,
                password=password,
                timeout=10,
                look_for_keys=False,
                allow_agent=False
            )
            self.sftp = self.ssh.open_sftp()
            self.current_path = "/"
            return True
        except Exception:
            return False

    def disconnect(self):
        if self.sftp:
            self.sftp.close()
        if self.ssh:
            self.ssh.close()
        self.ssh = self.sftp = None
        self.current_path = "/"

    def is_connected(self) -> bool:
        return self.sftp is not None

    def get_folders(self) -> List[str]:
        if not self.sftp:
            return []
        folders = []
        try:
            if self.current_path != "/":
                folders.append("..")
            entries = self.sftp.listdir_attr(self.current_path)
            for attr in entries:
                if (attr.st_mode & 0o040000) and not attr.filename.startswith('.'):
                    folders.append(attr.filename)
            folders.sort(key=str.lower)
        except Exception:
            pass
        return folders

    def get_files(self) -> List[Tuple[str, int]]:
        if not self.sftp:
            return []
        files = []
        try:
            entries = self.sftp.listdir_attr(self.current_path)
            for attr in entries:
                if not (attr.st_mode & 0o040000) and not attr.filename.startswith('.'):
                    files.append((attr.filename, attr.st_size))
            files.sort(key=lambda x: x[0].lower())
        except Exception:
            pass
        return files

    def navigate_to(self, folder_name: str) -> bool:
        try:
            folder_name = folder_name.strip()
            if folder_name == "..":
                if self.current_path == "/":
                    return False
                parts = self.current_path.rstrip("/").split("/")
                new_path = "/".join(parts[:-1]) or "/"
            else:
                new_path = f"{self.current_path.rstrip('/')}/{folder_name}"

            self.sftp.listdir(new_path)
            self.current_path = new_path
            return True
        except Exception:
            return False

    def upload_file(self, local_path: str, remote_filename: str) -> bool:
        """Upload a file from local path to remote server"""
        if not self.sftp:
            return False
        try:
            self.sftp.put(local_path, f"{self.current_path.rstrip('/')}/{remote_filename}")
            return True
        except Exception:
            return False

    def download_file(self, remote_filename: str, local_path: str) -> bool:
        """Download a file from remote server to local path"""
        if not self.sftp:
            return False
        try:
            self.sftp.get(f"{self.current_path.rstrip('/')}/{remote_filename}", local_path)
            return True
        except Exception:
            return False