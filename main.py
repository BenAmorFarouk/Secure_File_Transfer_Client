import customtkinter as ctk
import threading
import os
from gui import SFTPInterface
from local_fs import LocalFileSystem
from remote_sftp import RemoteSFTP


class SFTPApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Secure SFTP Client")
        self.root.geometry("1280x720")

        self.local_fs = LocalFileSystem()
        self.remote_sftp = RemoteSFTP()

        self.gui = SFTPInterface(self.root)
        self._bind_events()

        self._refresh_local()
        self._refresh_remote()
        self.gui.log("Ready. Enter credentials and connect securely.")
        self.remote_sftp.ask_trust_callback = self._ask_trust_host
        self.remote_sftp.log_callback = self.gui.log

    def _bind_events(self):
        self.gui.on_connect_callback = self.connect
        self.gui.on_disconnect_callback = self.disconnect
        self.gui.on_upload_callback = self.upload
        self.gui.on_download_callback = self.download
        self.gui.on_view_local_file_callback = self.view_local_file
        self.gui.on_view_remote_file_callback = self.view_remote_file
        self.gui._on_local_folder_select = self._local_folder_selected
        self.gui._on_remote_folder_select = self._remote_folder_selected

    def _ask_trust_host(self, host: str, fingerprint: str) -> bool:
        """Run the trust dialog on the main GUI thread and wait for user input."""
        result = {"value": False}
        event = threading.Event()

        def ask():
            try:
                result["value"] = self.gui.ask_trust_host(host, fingerprint)
            finally:
                event.set()

        self.root.after(0, ask)
        event.wait()
        return result["value"]

    def _refresh_local(self):
        folders = self.local_fs.get_folders()
        folder_text = "\n".join(f"[DIR]  {name}" for name in folders)
        self.gui.update_local_tree(folder_text)

        files = self.local_fs.get_files()
        self.gui.update_local_files(files)

        self.gui.local_folder_label.configure(text=f"Local: {self.local_fs.current_folder}")

    def _refresh_remote(self):
        if not self.remote_sftp.is_connected():
            self.gui.update_remote_tree("Not connected")
            self.gui.update_remote_files([])
            self.gui.remote_folder_label.configure(text="Remote Folders")
            return

        folders = self.remote_sftp.get_folders()
        folder_text = "\n".join(f"[DIR]  {name}" for name in folders)
        self.gui.update_remote_tree(folder_text)

        files = self.remote_sftp.get_files()
        self.gui.update_remote_files(files)

        self.gui.remote_folder_label.configure(text=f"Remote: {self.remote_sftp.current_path}")

    def _local_folder_selected(self, folder_name: str):
        if self.local_fs.navigate_to(folder_name):
            self._refresh_local()
            self.gui.log(f"Local: {self.local_fs.current_folder}")
        else:
            self.gui.log(f"Cannot enter: {folder_name}")

    def _remote_folder_selected(self, folder_name: str):
        if self.remote_sftp.navigate_to(folder_name):
            self._refresh_remote()
            self.gui.log(f"Remote: {self.remote_sftp.current_path}")
        else:
            self.gui.log(f"Remote: Cannot enter '{folder_name}'")

    def connect(self):
        creds = self.gui.get_credentials()
        host = creds["host"].strip()
        user = creds["user"].strip()
        if not host or not user or not creds["port"]:
            self.gui.log("Host, port, and user required.")
            return
        if any(c.isspace() for c in host):
            self.gui.log("Host may not contain whitespace.")
            return
        if any(c.isspace() for c in user):
            self.gui.log("Username may not contain whitespace.")
            return
        try:
            port = int(creds["port"])
            if port < 1 or port > 65535:
                raise ValueError()
        except ValueError:
            self.gui.log("Port must be a number between 1 and 65535.")
            return

        key_file = creds.get("key_path", None)
        password = creds["password"]
        self.gui.clear_password()

        if key_file:
            self.gui.log("Using SSH private key authentication.")
        else:
            self.gui.log("Using password authentication.")

        password_bytes = bytearray(password.encode("utf-8")) if password else None

        def _connect_thread(password_bytes):
            password_str = password_bytes.decode("utf-8") if password_bytes else None
            success = False
            try:
                success = self.remote_sftp.connect(
                    host, port, user, password_str, key_filename=key_file
                )
            finally:
                if password_bytes is not None:
                    for i in range(len(password_bytes)):
                        password_bytes[i] = 0
            self.root.after(0, lambda: self._on_connect_result(success))

        creds["password"] = None
        password = None
        self.gui.connect_btn.configure(state="disabled")
        threading.Thread(target=_connect_thread, args=(password_bytes,), daemon=True).start()

    def _on_connect_result(self, success: bool):
        if success:
            self.gui.set_connected(True)
            self._refresh_remote()
            self.gui.log("Secure connection established.")
        else:
            self.gui.log("Connection failed. Check credentials & server host key.")
            self.gui.connect_btn.configure(state="normal")

    def disconnect(self):
        self.remote_sftp.disconnect()
        self.gui.set_connected(False)
        self.gui.clear_password()
        self._refresh_remote()
        self.gui.log("Disconnected securely.")

    def upload(self):
        if not self.remote_sftp.is_connected():
            self.gui.log("Not connected to remote server")
            return

        filename = self.gui.get_selected_local_file()
        if not filename:
            self.gui.log("No local file selected. Double-click a local file to select it.")
            return

        local_path = self.local_fs.get_selected_file(filename)
        if not local_path:
            self.gui.log(f"File not found: {filename}")
            return

        def _upload_thread():
            success = self.remote_sftp.upload_file(local_path, filename)
            self.root.after(0, lambda: self._on_upload_result(success, filename))

        self.gui.log(f"Uploading {filename} securely...")
        threading.Thread(target=_upload_thread, daemon=True).start()

    def _on_upload_result(self, success: bool, filename: str):
        if success:
            self.gui.log(f"Successfully uploaded {filename}")
            self._refresh_remote()
        else:
            self.gui.log(f"Failed to upload {filename}")

    def download(self):
        if not self.remote_sftp.is_connected():
            self.gui.log("Not connected to remote server")
            return

        filename = self.gui.get_selected_remote_file()
        if not filename:
            self.gui.log("No remote file selected. Double-click a remote file to select it.")
            return

        local_path = os.path.join(self.local_fs.get_full_path(), filename)

        def _download_thread():
            success = self.remote_sftp.download_file(filename, local_path)
            self.root.after(0, lambda: self._on_download_result(success, filename))

        self.gui.log(f"Downloading {filename} securely...")
        threading.Thread(target=_download_thread, daemon=True).start()

    def _on_download_result(self, success: bool, filename: str):
        if success:
            self.gui.log(f"Successfully downloaded {filename}")
            self._refresh_local()
        else:
            self.gui.log(f"Failed to download {filename}")

    def view_local_file(self):
        """Open and display the contents of a selected local file"""
        filename = self.gui.get_selected_local_file()
        if not filename:
            self.gui.log("No local file selected. Click a file to select it first.")
            return

        content = self.local_fs.read_file_content(filename)
        self.gui.show_file_viewer(filename, content)
        self.gui.log(f"Opened: {filename}")

    def view_remote_file(self):
        """Open and display the contents of a selected remote file"""
        if not self.remote_sftp.is_connected():
            self.gui.log("Not connected to remote server")
            return

        filename = self.gui.get_selected_remote_file()
        if not filename:
            self.gui.log("No remote file selected. Click a file to select it first.")
            return

        content = self.remote_sftp.read_file_content(filename)
        self.gui.show_file_viewer(filename, content)
        self.gui.log(f"Opened: {filename}")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = SFTPApp()
    app.run()
