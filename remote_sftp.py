import base64
import hashlib
import logging
import os
import paramiko
import posixpath
from typing import Callable, List, Tuple, Optional

logger = logging.getLogger(__name__)


class RemoteSFTP:
    def __init__(self, known_hosts_path: str = os.path.expanduser("~/.ssh/known_hosts")):
        self.ssh: Optional[paramiko.SSHClient] = None
        self.sftp: Optional[paramiko.SFTPClient] = None
        self.current_path = "/"
        self.known_hosts_path = known_hosts_path
        self.ask_trust_callback: Optional[Callable[[str, str], bool]] = None
        self.max_preview_bytes = 2 * 1024 * 1024  # limit preview to 2 MB

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
            self._ensure_known_hosts_permissions()
            self._load_known_hosts()

            # Reject unknown host keys by default
            self.ssh.set_missing_host_key_policy(paramiko.RejectPolicy())

            # Attempt secure SSH connection with timeouts and disabled legacy algorithms
            self.ssh.connect(
                hostname=host,
                port=port,
                username=username,
                password=password,
                key_filename=key_filename,
                timeout=10,
                banner_timeout=10,
                auth_timeout=10,
                look_for_keys=False,
                allow_agent=False,
                disabled_algorithms={
                    'cipher': [
                        '3des-cbc', 'blowfish-cbc', 'cast128-cbc',
                        'arcfour', 'arcfour128', 'arcfour256'
                    ],
                    'mac': [
                        'hmac-md5', 'hmac-md5-96', 'hmac-sha1', 'hmac-sha1-96'
                    ],
                    'kex': [
                        'diffie-hellman-group1-sha1',
                        'diffie-hellman-group14-sha1',
                        'diffie-hellman-group-exchange-sha1'
                    ],
                    'pubkeys': [
                        'ssh-rsa'
                    ]
                }
            )

            self.sftp = self.ssh.open_sftp()
            self.current_path = "/"
            print(f"[+] Connected securely to {host}:{port} as {username}")
            return True

        except paramiko.BadHostKeyException:
            print("[!] Host key mismatch — possible MITM attack.")
        except paramiko.AuthenticationException:
            print("[!] Authentication failed — check username, password, or SSH key.")
        except paramiko.SSHException as e:
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
                banner_timeout=10,
                auth_timeout=10,
                look_for_keys=False,
                allow_agent=False,
                disabled_algorithms={
                    'cipher': [
                        '3des-cbc', 'blowfish-cbc', 'cast128-cbc',
                        'arcfour', 'arcfour128', 'arcfour256'
                    ],
                    'mac': [
                        'hmac-md5', 'hmac-md5-96', 'hmac-sha1', 'hmac-sha1-96'
                    ],
                    'kex': [
                        'diffie-hellman-group1-sha1',
                        'diffie-hellman-group14-sha1',
                        'diffie-hellman-group-exchange-sha1'
                    ],
                    'pubkeys': [
                        'ssh-rsa'
                    ]
                }
            )

            transport = temp_client.get_transport()
            if transport is None:
                raise RuntimeError("Remote transport unavailable after connection")
            key = transport.get_remote_server_key()
            md5_fingerprint = ":".join(f"{b:02x}" for b in key.get_fingerprint())
            sha256_fingerprint = self._compute_host_key_sha256(key)

            if self.ask_trust_callback:
                decision = self.ask_trust_callback(host, sha256_fingerprint)
            else:
                print(f"Unknown host: {host}\nSHA256: {sha256_fingerprint}\nMD5: {md5_fingerprint}")
                decision = input(f"Trust this server and add to known_hosts? (yes/no): ").strip().lower().startswith("y")

            if decision:
                self._save_known_host_entry(host, key)
                return True
            return False

        except Exception as e:
            print(f"[!] Could not verify host key: {e}")
            return False
        finally:
            temp_client.close()

    def _ensure_known_hosts_permissions(self):
        """Ensure ~/.ssh and known_hosts are created with secure permissions."""
        try:
            known_hosts_dir = os.path.dirname(self.known_hosts_path)
            if known_hosts_dir:
                os.makedirs(known_hosts_dir, exist_ok=True)
                if os.name != "nt":
                    os.chmod(known_hosts_dir, 0o700)
                else:
                    logger.debug("Windows cannot enforce POSIX permissions for %s", known_hosts_dir)
            if os.path.exists(self.known_hosts_path):
                if os.name != "nt":
                    os.chmod(self.known_hosts_path, 0o600)
                else:
                    logger.debug("Windows cannot enforce POSIX permissions for %s", self.known_hosts_path)
        except Exception as e:
            logger.warning("Could not set known_hosts permissions: %s", e)

    def _load_known_hosts(self):
        """Load known_hosts from disk if available."""
        try:
            if os.path.exists(self.known_hosts_path):
                self.ssh.load_host_keys(self.known_hosts_path)
            else:
                logger.debug("No known_hosts file found at %s", self.known_hosts_path)
        except Exception as e:
            logger.warning("Could not load known_hosts file %s: %s", self.known_hosts_path, e)

    def _save_known_host_entry(self, host: str, key: paramiko.PKey):
        """Write the host key to known_hosts in OpenSSH format."""
        try:
            os.makedirs(os.path.dirname(self.known_hosts_path), exist_ok=True)
            with open(self.known_hosts_path, "a", encoding="utf-8") as f:
                entry = f"{host} {key.get_name()} {key.get_base64()}\n"
                f.write(entry)
            if os.name != "nt":
                os.chmod(self.known_hosts_path, 0o600)
        except Exception as e:
            logger.warning("Failed to write known_hosts entry: %s", e)

    def _compute_host_key_sha256(self, key: paramiko.PKey) -> str:
        """Compute a SHA-256 fingerprint for a host key in OpenSSH format."""
        try:
            raw = base64.b64decode(key.get_base64())
            digest = hashlib.sha256(raw).digest()
            fingerprint = base64.b64encode(digest).decode("ascii").rstrip("=")
            return f"SHA256:{fingerprint}"
        except Exception:
            # Fallback to the legacy MD5-style fingerprint if SHA256 cannot be computed
            return ":".join(f"{b:02x}" for b in key.get_fingerprint())

    def _compute_sha256(self, path: str, remote: bool = False) -> Optional[str]:
        """Compute SHA-256 digest for a local or remote file."""
        try:
            digest = hashlib.sha256()
            if remote:
                with self.sftp.file(path, "rb") as f:
                    while True:
                        chunk = f.read(65536)
                        if not chunk:
                            break
                        digest.update(chunk)
            else:
                with open(path, "rb") as f:
                    while chunk := f.read(65536):
                        digest.update(chunk)
            return digest.hexdigest()
        except Exception as e:
            logger.warning("Integrity check failed for %s: %s", path, e)
            return None

    def _verify_transfer_integrity(self, local_path: str, remote_path: str) -> bool:
        local_hash = self._compute_sha256(local_path)
        remote_hash = self._compute_sha256(remote_path, remote=True)
        if local_hash is None or remote_hash is None:
            return False
        if local_hash != remote_hash:
            logger.warning("Transfer integrity mismatch: local=%s remote=%s", local_hash, remote_hash)
            return False
        return True

    def _join_remote_path(self, filename: str) -> str:
        """Build a normalized, safe remote file path under the current directory."""
        clean_name = filename.strip()
        if not clean_name or clean_name in {".", ".."}:
            raise ValueError("Invalid remote filename")
        if "/" in clean_name or "\\" in clean_name:
            raise ValueError("Invalid remote filename")
        if any(ord(c) < 32 for c in clean_name):
            raise ValueError("Invalid remote filename")

        sanitized = posixpath.basename(clean_name)
        if not sanitized or sanitized in {".", ".."}:
            raise ValueError("Invalid remote filename")

        if self.current_path == "/":
            return f"/{sanitized}"

        return posixpath.normpath(posixpath.join(self.current_path, sanitized))

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
        sftp = self.sftp
        folders = []
        try:
            if self.current_path != "/":
                folders.append("..")
            entries = sftp.listdir_attr(self.current_path)
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
        sftp = self.sftp
        files = []
        try:
            entries = sftp.listdir_attr(self.current_path)
            for attr in entries:
                if not (attr.st_mode & 0o040000) and not attr.filename.startswith('.'):
                    files.append((attr.filename, attr.st_size))
            files.sort(key=lambda x: x[0].lower())
        except Exception as e:
            print(f"[!] Error listing files: {e}")
        return files

    def navigate_to(self, folder_name: str) -> bool:
        """Navigate securely to another directory."""
        if not self.sftp:
            return False
        sftp = self.sftp
        try:
            folder_name = folder_name.strip()
            if folder_name == "..":
                if self.current_path == "/":
                    return False
                parts = self.current_path.rstrip("/").split("/")
                new_path = "/".join(parts[:-1]) or "/"
            else:
                if "/" in folder_name or "\\" in folder_name:
                    return False
                new_path = posixpath.normpath(f"{self.current_path}/{folder_name}")

            sftp.listdir(new_path)
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
            remote_path = self._join_remote_path(remote_filename)
            self.sftp.put(local_path, remote_path)

            local_size = os.path.getsize(local_path)
            remote_stat = self.sftp.stat(remote_path)
            if local_size != remote_stat.st_size:
                print("[!] Upload verification failed: file sizes differ.")
                return False

            if local_size <= self.max_preview_bytes:
                if not self._verify_transfer_integrity(local_path, remote_path):
                    print("[!] Upload verification failed: checksum mismatch.")
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
            remote_path = self._join_remote_path(remote_filename)
            self.sftp.get(remote_path, local_path)

            local_size = os.path.getsize(local_path)
            remote_stat = self.sftp.stat(remote_path)
            if local_size != remote_stat.st_size:
                print("[!] Download verification failed: file sizes differ.")
                return False

            if local_size <= self.max_preview_bytes:
                if not self._verify_transfer_integrity(local_path, remote_path):
                    print("[!] Download verification failed: checksum mismatch.")
                    return False

            print(f"[+] Downloaded {remote_filename}")
            return True
        except Exception as e:
            print(f"[!] Download failed: {e}")
            return False

    def read_file_content(self, filename: str) -> str:
        """Read the content of a remote file. Returns content or error message."""
        if not self.sftp:
            return "Error: Not connected to remote server"
        sftp = self.sftp

        try:
            remote_path = self._join_remote_path(filename)
            remote_stat = sftp.stat(remote_path)
            if remote_stat.st_size > self.max_preview_bytes:
                return f"File too large to preview ({remote_stat.st_size} bytes)."

            with self.sftp.file(remote_path, 'r') as f:
                content = f.read().decode('utf-8', errors='replace')
            return content
        except Exception as e:
            return f"Error reading file: {str(e)}"
