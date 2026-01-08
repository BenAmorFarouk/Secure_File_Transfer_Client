import paramiko
import os
import posixpath
from typing import List, Tuple, Optional


class RemoteSFTP:
    def __init__(self, known_hosts_path: str = os.path.expanduser("~/.ssh/known_hosts")):
        self.ssh: Optional[paramiko.SSHClient] = None
        self.sftp: Optional[paramiko.SFTPClient] = None
        self.current_path = "/"
        self.known_hosts_path = known_hosts_path
        self.ask_trust_callback: Optional[Callable[[str, str], bool]] = None

    def connect(
        self,
        host: str,
        port: int,
        username: str,
        password: Optional[str] = None,
        key_filename: Optional[str] = None,
    ) -> bool:
        """Connect securely to an SFTP server with host key verification and optional user trust."""
        try:
            self.ssh = paramiko.SSHClient()

            # Load known_hosts file if exists
            if os.path.exists(self.known_hosts_path):
                self.ssh.load_host_keys(self.known_hosts_path)
            else:
                print(f"[!] No known_hosts file found at {self.known_hosts_path}")

            # Reject unknown host keys by default
            self.ssh.set_missing_host_key_policy(paramiko.RejectPolicy())

            # Attempt secure SSH connection
            self.ssh.connect(
                hostname=host,
                port=port,
                username=username,
                password=password,
                key_filename=key_filename,
                timeout=10,
                look_for_keys=False,
                allow_agent=False
            )

            self.sftp = self.ssh.open_sftp()
            self.current_path = "/"
            print(f"[+] Connected securely to {host}:{port} as {username}")
            return True

        except paramiko.ssh_exception.BadHostKeyException:
            print("[!] Host key mismatch — possible MITM attack.")
        except paramiko.ssh_exception.AuthenticationException:
            print("[!] Authentication failed — check username, password, or SSH key.")
        except paramiko.ssh_exception.SSHException as e:
            if "not found in known_hosts" in str(e).lower() or "unknown server" in str(e).lower():
                print(f"[?] Unknown host: {host}")
                if self._attempt_trust_prompt(host, port, username, password, key_filename):
                    return self.connect(host, port, username, password, key_filename)
                else:
                    print("[!] Connection aborted.")
                    self.disconnect()
                    return False
            else:
                print(f"[!] SSH error: {e}")
        except Exception as e:
            print(f"[!] Connection failed: {e}")

        # Cleanup partial connections
        self.disconnect()
        return False

    def _attempt_trust_prompt(
            self, host: str, port: int, username: str, password: Optional[str], key_filename: Optional[str]
    ) -> bool:
        """Prompt user to trust unknown host key, using GUI if callback is set."""
        temp_client = paramiko.SSHClient()
        temp_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            temp_client.connect(
                hostname=host,
                port=port,
                username=username,
                password=password,
                key_filename=key_filename,
                timeout=10,
                look_for_keys=False,
                allow_agent=False
            )

            key = temp_client.get_transport().get_remote_server_key()
            fingerprint = ":".join(f"{b:02x}" for b in key.get_fingerprint())

            if self.ask_trust_callback:
                decision = self.ask_trust_callback(host, fingerprint)
            else:
                decision = input(f"Trust this server and add to known_hosts? (yes/no): ").strip().lower().startswith(
                    "y")

            if decision:
                self._save_known_host_entry(host, key)
                return True
            return False

        except Exception as e:
            print(f"[!] Could not verify host key: {e}")
            return False
        finally:
            temp_client.close()
    def _save_known_host_entry(self, host: str, key: paramiko.PKey):
        """Write the host key to known_hosts in OpenSSH format."""
        try:
            os.makedirs(os.path.dirname(self.known_hosts_path), exist_ok=True)
            with open(self.known_hosts_path, "a", encoding="utf-8") as f:
                entry = f"{host} {key.get_name()} {key.get_base64()}\n"
                f.write(entry)
        except Exception as e:
            print(f"[!] Failed to write known_hosts entry: {e}")

    def disconnect(self):
        """Close the SFTP and SSH connections cleanly."""
        try:
            if self.sftp:
                self.sftp.close()
            if self.ssh:
                self.ssh.close()
        finally:
            self.ssh = self.sftp = None
            self.current_path = "/"

    def is_connected(self) -> bool:
        return self.sftp is not None

    def get_folders(self) -> List[str]:
        """Return list of folders in the current remote directory."""
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
        except Exception as e:
            print(f"[!] Error listing folders: {e}")
        return folders

    def get_files(self) -> List[Tuple[str, int]]:
        """Return list of (filename, size) tuples in the current directory."""
        if not self.sftp:
            return []
        files = []
        try:
            entries = self.sftp.listdir_attr(self.current_path)
            for attr in entries:
                if not (attr.st_mode & 0o040000) and not attr.filename.startswith('.'):
                    files.append((attr.filename, attr.st_size))
            files.sort(key=lambda x: x[0].lower())
        except Exception as e:
            print(f"[!] Error listing files: {e}")
        return files

    def navigate_to(self, folder_name: str) -> bool:
        """Navigate securely to another directory."""
        try:
            folder_name = folder_name.strip()
            if folder_name == "..":
                if self.current_path == "/":
                    return False
                parts = self.current_path.rstrip("/").split("/")
                new_path = "/".join(parts[:-1]) or "/"
            else:
                new_path = posixpath.normpath(f"{self.current_path}/{folder_name}")

            self.sftp.listdir(new_path)
            self.current_path = new_path
            return True
        except Exception as e:
            print(f"[!] Cannot navigate to {folder_name}: {e}")
            return False

    def upload_file(self, local_path: str, remote_filename: str) -> bool:
        """Upload a file with basic integrity check."""
        if not self.sftp:
            return False
        try:
            remote_path = f"{self.current_path.rstrip('/')}/{remote_filename}"
            self.sftp.put(local_path, remote_path)

            remote_stat = self.sftp.stat(remote_path)
            if os.path.getsize(local_path) != remote_stat.st_size:
                print("[!] Upload verification failed: file sizes differ.")
                return False

            print(f"[+] Uploaded {remote_filename}")
            return True
        except Exception as e:
            print(f"[!] Upload failed: {e}")
            return False

    def download_file(self, remote_filename: str, local_path: str) -> bool:
        """Download a file with basic integrity check."""
        if not self.sftp:
            return False
        try:
            remote_path = f"{self.current_path.rstrip('/')}/{remote_filename}"
            self.sftp.get(remote_path, local_path)

            remote_stat = self.sftp.stat(remote_path)
            if os.path.getsize(local_path) != remote_stat.st_size:
                print("[!] Download verification failed: file sizes differ.")
                return False

            print(f"[+] Downloaded {remote_filename}")
            return True
        except Exception as e:
            print(f"[!] Download failed: {e}")
            return False
