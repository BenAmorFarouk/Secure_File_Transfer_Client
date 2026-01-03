import customtkinter as ctk
import threading
from gui import SFTPInterface
from local_fs import LocalFileSystem
from remote_sftp import RemoteSFTP

class SFTPApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("SFTP Client")
        self.root.geometry("1280x720")

        self.local_fs = LocalFileSystem()
        self.remote_sftp = RemoteSFTP()

        self.gui = SFTPInterface(self.root)
        self._bind_events()

        self._refresh_local()
        self._refresh_remote()
        self.gui.log("Ready. Enter credentials and connect.")

    def _bind_events(self):
        self.gui.on_connect_callback = self.connect
        self.gui.on_disconnect_callback = self.disconnect
        self.gui.on_upload_callback = self.upload
        self.gui.on_download_callback = self.download
        self.gui._on_local_folder_select = self._local_folder_selected
        self.gui._on_remote_folder_select = self._remote_folder_selected

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
        if not all([creds["host"], creds["port"], creds["user"]]):
            self.gui.log("Host, port, and user required.")
            return
        try:
            port = int(creds["port"])
        except ValueError:
            self.gui.log("Port must be a number.")
            return

        def _connect_thread():
            success = self.remote_sftp.connect(
                creds["host"], port, creds["user"], creds["password"]
            )
            self.root.after(0, lambda: self._on_connect_result(success))

        self.gui.connect_btn.configure(state="disabled")
        threading.Thread(target=_connect_thread, daemon=True).start()

    def _on_connect_result(self, success: bool):
        if success:
            self.gui.set_connected(True)
            self._refresh_remote()
            self.gui.log("Connected to remote server.")
        else:
            self.gui.log("Connection failed. Check credentials & server.")
            self.gui.connect_btn.configure(state="normal")

    def disconnect(self):
        self.remote_sftp.disconnect()
        self.gui.set_connected(False)
        self._refresh_remote()
        self.gui.log("Disconnected.")

    def upload(self):
        self.gui.log("Upload: Not implemented")

    def download(self):
        self.gui.log("Download: Not implemented")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = SFTPApp()
    app.run()