import customtkinter as ctk
from typing import Callable, Optional
from PIL import Image
import os

class SFTPInterface:
    def __init__(self, root: ctk.CTk):
        self.root = root
        self.on_connect_callback: Optional[Callable] = None
        self.on_disconnect_callback: Optional[Callable] = None
        self.on_upload_callback: Optional[Callable] = None
        self.on_download_callback: Optional[Callable] = None
        self.on_view_local_file_callback: Optional[Callable] = None
        self.on_view_remote_file_callback: Optional[Callable] = None
        self.selected_local_file: Optional[str] = None
        self.selected_remote_file: Optional[str] = None
        self._build_ui()

    def _build_ui(self):
        # Header with Logo
        self.header_frame = ctk.CTkFrame(self.root, height=80)
        self.header_frame.pack(fill="x", padx=15, pady=(15, 8))
        self.header_frame.pack_propagate(False)
        
        # Logo on the left
        logo_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=(0, 15), pady=10, sticky="w")
        
        try:
            # Load and display the high-resolution logo
            logo_path = os.path.join(os.path.dirname(__file__), "high-resolution-color-logo.png")
            if os.path.exists(logo_path):
                logo_image = Image.open(logo_path)
                logo_image.thumbnail((60, 60), Image.Resampling.LANCZOS)
                self.logo_photo = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(60, 60))
                logo_label = ctk.CTkLabel(logo_frame, image=self.logo_photo, text="")
                logo_label.pack()
        except Exception as e:
            print(f"Could not load logo: {e}")
        
        # Connection form frame (rest of header)
        self.header_frame.grid_columnconfigure(2, weight=1)
        self.header_frame.grid_columnconfigure(6, weight=1)
        self.header_frame.grid_columnconfigure(8, weight=1)

        ctk.CTkLabel(self.header_frame, text="Host:", font=("Segoe UI", 13)).grid(row=0, column=1, padx=(10, 5), pady=10, sticky="w")
        self.host_entry = ctk.CTkEntry(self.header_frame, placeholder_text="e.g., 192.168.1.25")
        self.host_entry.grid(row=0, column=2, padx=5, pady=10, sticky="ew")
        self.host_entry.insert(0, "127.0.0.1")

        ctk.CTkLabel(self.header_frame, text="Port:").grid(row=0, column=3, padx=5, pady=10, sticky="w")
        self.port_entry = ctk.CTkEntry(self.header_frame, width=60)
        self.port_entry.grid(row=0, column=4, padx=5, pady=10)
        self.port_entry.insert(0, "22")

        ctk.CTkLabel(self.header_frame, text="User:").grid(row=0, column=5, padx=10, pady=10, sticky="w")
        self.user_entry = ctk.CTkEntry(self.header_frame)
        self.user_entry.grid(row=0, column=6, padx=5, pady=10, sticky="ew")
        self.user_entry.insert(0, "user")

        ctk.CTkLabel(self.header_frame, text="Key:").grid(row=0, column=7, padx=10, pady=10, sticky="w")
        self.key_path_entry = ctk.CTkEntry(self.header_frame, placeholder_text="Optional key file")
        self.key_path_entry.grid(row=0, column=8, padx=5, pady=10, sticky="ew")

        ctk.CTkLabel(self.header_frame, text="Pass:").grid(row=0, column=9, padx=10, pady=10, sticky="w")
        self.pass_entry = ctk.CTkEntry(self.header_frame, show="•", width=120)
        self.pass_entry.grid(row=0, column=10, padx=5, pady=10)

        self.connect_btn = ctk.CTkButton(self.header_frame, text="Connect", width=100, command=self._on_connect)
        self.connect_btn.grid(row=0, column=11, padx=(10, 5), pady=10)

        self.disconnect_btn = ctk.CTkButton(self.header_frame, text="Disconnect", width=100, state="disabled", command=self._on_disconnect)
        self.disconnect_btn.grid(row=0, column=12, padx=(5, 10), pady=10)

        # Main area
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=15, pady=(0, 12))
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1, minsize=450)
        main_frame.grid_columnconfigure(1, weight=0, minsize=120)
        main_frame.grid_columnconfigure(2, weight=1, minsize=450)

        # Local side
        local_frame = ctk.CTkFrame(main_frame)
        local_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        local_frame.grid_rowconfigure(0, weight=1)
        local_frame.grid_rowconfigure(1, weight=1)
        local_frame.grid_columnconfigure(0, weight=1)

        local_tree_section = ctk.CTkFrame(local_frame)
        local_tree_section.grid(row=0, column=0, sticky="nsew", padx=8, pady=(8, 4))
        local_tree_section.grid_rowconfigure(1, weight=1)
        local_tree_section.grid_columnconfigure(0, weight=1)

        self.local_folder_label = ctk.CTkLabel(local_tree_section, text="Local Folders", font=("Segoe UI", 13, "bold"), anchor="w")
        self.local_folder_label.grid(row=0, column=0, sticky="ew", padx=4, pady=(4, 2))
        self.local_tree = ctk.CTkTextbox(local_tree_section, font=("Consolas", 11), wrap="none")
        self.local_tree.grid(row=1, column=0, sticky="nsew", padx=2, pady=(0, 4))
        self.local_tree.bind("<ButtonRelease-1>", self._on_local_tree_click)

        local_files_section = ctk.CTkFrame(local_frame)
        local_files_section.grid(row=1, column=0, sticky="nsew", padx=8, pady=(4, 8))
        local_files_section.grid_rowconfigure(1, weight=1)
        local_files_section.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(local_files_section, text="Local Files", font=("Segoe UI", 13, "bold"), anchor="w").grid(row=0, column=0, sticky="ew", padx=4, pady=(4, 2))
        self.local_files = ctk.CTkTextbox(local_files_section, font=("Consolas", 11), wrap="none")
        self.local_files.grid(row=1, column=0, sticky="nsew", padx=2, pady=(0, 4))
        self.local_files.bind("<Double-Button-1>", self._on_local_file_double_click)
        self.local_files.bind("<ButtonRelease-1>", self._on_local_file_click)

        # View file button
        local_btn_frame = ctk.CTkFrame(local_files_section)
        local_btn_frame.grid(row=2, column=0, sticky="ew", padx=2, pady=2)
        self.view_local_btn = ctk.CTkButton(local_btn_frame, text="View File", height=30, command=self._on_view_local_file)
        self.view_local_btn.pack(side="left", padx=2)

        # Action buttons
        btn_frame = ctk.CTkFrame(main_frame, width=120)
        btn_frame.grid(row=0, column=1, padx=6)


        self.download_btn = ctk.CTkButton(btn_frame, text="Download", width=100, height=40, state="disabled", command=self._on_download)
        self.download_btn.pack(pady=10)

        self.upload_btn = ctk.CTkButton(btn_frame, text="Upload", width=100, height=40, state="disabled", command=self._on_upload)
        self.upload_btn.pack(pady=10)

        # Remote side
        remote_frame = ctk.CTkFrame(main_frame)
        remote_frame.grid(row=0, column=2, sticky="nsew", padx=(6, 0))
        remote_frame.grid_rowconfigure(0, weight=1)
        remote_frame.grid_rowconfigure(1, weight=1)
        remote_frame.grid_columnconfigure(0, weight=1)

        remote_tree_section = ctk.CTkFrame(remote_frame)
        remote_tree_section.grid(row=0, column=0, sticky="nsew", padx=8, pady=(8, 4))
        remote_tree_section.grid_rowconfigure(1, weight=1)
        remote_tree_section.grid_columnconfigure(0, weight=1)

        self.remote_folder_label = ctk.CTkLabel(remote_tree_section, text="Remote Folders", font=("Segoe UI", 13, "bold"), anchor="w")
        self.remote_folder_label.grid(row=0, column=0, sticky="ew", padx=4, pady=(4, 2))
        self.remote_tree = ctk.CTkTextbox(remote_tree_section, font=("Consolas", 11), wrap="none")
        self.remote_tree.grid(row=1, column=0, sticky="nsew", padx=2, pady=(0, 4))
        self.remote_tree.bind("<ButtonRelease-1>", self._on_remote_tree_click)

        remote_files_section = ctk.CTkFrame(remote_frame)
        remote_files_section.grid(row=1, column=0, sticky="nsew", padx=8, pady=(4, 8))
        remote_files_section.grid_rowconfigure(1, weight=1)
        remote_files_section.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(remote_files_section, text="Remote Files", font=("Segoe UI", 13, "bold"), anchor="w").grid(row=0, column=0, sticky="ew", padx=4, pady=(4, 2))
        self.remote_files = ctk.CTkTextbox(remote_files_section, font=("Consolas", 11), wrap="none")
        self.remote_files.grid(row=1, column=0, sticky="nsew", padx=2, pady=(0, 4))
        self.remote_files.bind("<Double-Button-1>", self._on_remote_file_double_click)
        self.remote_files.bind("<ButtonRelease-1>", self._on_remote_file_click)

        # View file button
        remote_btn_frame = ctk.CTkFrame(remote_files_section)
        remote_btn_frame.grid(row=2, column=0, sticky="ew", padx=2, pady=2)
        self.view_remote_btn = ctk.CTkButton(remote_btn_frame, text="View File", height=30, command=self._on_view_remote_file)
        self.view_remote_btn.pack(side="left", padx=2)

        # Log
        ctk.CTkLabel(self.root, text="Log", font=("Segoe UI", 12, "bold"), anchor="w").pack(fill="x", padx=15, pady=(0, 2))
        self.log_text = ctk.CTkTextbox(self.root, height=100, font=("Consolas", 10), state="disabled")
        self.log_text.pack(fill="x", padx=15, pady=(0, 12))

    def get_credentials(self):
        return {
            "host": self.host_entry.get().strip(),
            "port": self.port_entry.get().strip(),
            "user": self.user_entry.get().strip(),
            "password": self.pass_entry.get(),
            "key_path": self.key_path_entry.get().strip() or None
        }

    def clear_password(self):
        self.pass_entry.delete(0, "end")

    def log(self, msg: str):
        from utils import log_to_widget
        log_to_widget(self.log_text, msg)

    def update_local_tree(self, text: str):
        self.local_tree.configure(state="normal")
        self.local_tree.delete("0.0", "end")
        self.local_tree.insert("0.0", text)
        self.local_tree.configure(state="disabled")

    def update_local_files(self, files: list):
        self.local_files.configure(state="normal")
        self.local_files.delete("0.0", "end")
        for name, size in files:
            self.local_files.insert("end", f"[FILE] {name:<30} {self._human_size(size)}\n")
        self.local_files.configure(state="disabled")

    def update_remote_tree(self, text: str):
        self.remote_tree.configure(state="normal")
        self.remote_tree.delete("0.0", "end")
        self.remote_tree.insert("0.0", text)
        self.remote_tree.configure(state="disabled")

    def update_remote_files(self, files: list):
        self.remote_files.configure(state="normal")
        self.remote_files.delete("0.0", "end")
        for name, size in files:
            self.remote_files.insert("end", f"[FILE] {name:<30} {self._human_size(size)}\n")
        self.remote_files.configure(state="disabled")

    def set_connected(self, connected: bool):
        state = "normal" if connected else "disabled"
        self.upload_btn.configure(state=state)
        self.download_btn.configure(state=state)
        self.disconnect_btn.configure(state="normal" if connected else "disabled")
        self.connect_btn.configure(state="disabled" if connected else "normal")

    def _on_connect(self):
        if self.on_connect_callback:
            self.on_connect_callback()

    def _on_disconnect(self):
        if self.on_disconnect_callback:
            self.on_disconnect_callback()

    def _on_upload(self):
        if self.on_upload_callback:
            self.on_upload_callback()

    def _on_download(self):
        if self.on_download_callback:
            self.on_download_callback()

    def _on_local_tree_click(self, event):
        try:
            index = self.local_tree.index(f"@{event.x},{event.y}")
            line_num = int(index.split(".")[0])
            line = self.local_tree.get(f"{line_num}.0", f"{line_num}.end").strip()
            if not line or not line.startswith("[DIR]"):
                return
            name = line[5:].strip()
            if name and hasattr(self, '_on_local_folder_select'):
                self._on_local_folder_select(name)
        except Exception as e:
            self.log(f"Local folder click error: {e}")

    def _on_remote_tree_click(self, event):
        try:
            index = self.remote_tree.index(f"@{event.x},{event.y}")
            line_num = int(index.split(".")[0])
            line = self.remote_tree.get(f"{line_num}.0", f"{line_num}.end").strip()
            if not line or not line.startswith("[DIR]"):
                return
            name = line[5:].strip()
            if name and hasattr(self, '_on_remote_folder_select'):
                self._on_remote_folder_select(name)
        except Exception as e:
            self.log(f"Remote folder click error: {e}")

    def _on_local_file_click(self, event):
        try:
            index = self.local_files.index(f"@{event.x},{event.y}")
            line_num = int(index.split(".")[0])
            line = self.local_files.get(f"{line_num}.0", f"{line_num}.end").strip()
            if not line or not line.startswith("[FILE]"):
                self.selected_local_file = None
                return
            # Extract filename from "[FILE] filename size" format
            parts = line.strip().split()
            if len(parts) >= 2:
                self.selected_local_file = parts[1]
                self.log(f"Selected local file: {self.selected_local_file}")
        except Exception as e:
            self.log(f"Local file click error: {e}")

    def _on_remote_file_click(self, event):
        try:
            index = self.remote_files.index(f"@{event.x},{event.y}")
            line_num = int(index.split(".")[0])
            line = self.remote_files.get(f"{line_num}.0", f"{line_num}.end").strip()
            if not line or not line.startswith("[FILE]"):
                self.selected_remote_file = None
                return
            # Extract filename from "[FILE] filename size" format
            parts = line.strip().split()
            if len(parts) >= 2:
                self.selected_remote_file = parts[1]
                self.log(f"Selected remote file: {self.selected_remote_file}")
        except Exception as e:
            self.log(f"Remote file click error: {e}")

    def _on_local_file_double_click(self, event):
        filename = self.get_selected_local_file()
        if filename and hasattr(self, '_on_local_file_select'):
            self._on_local_file_select(filename)

    def _on_remote_file_double_click(self, event):
        filename = self.get_selected_remote_file()
        if filename and hasattr(self, '_on_remote_file_select'):
            self._on_remote_file_select(filename)

    def _human_size(self, size_bytes: int) -> str:
        if size_bytes == 0:
            return "0 B"
        units = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(units) - 1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.1f} {units[i]}"

    def get_selected_local_file(self) -> str:
        """Get the currently selected local file"""
        return self.selected_local_file

    def get_selected_remote_file(self) -> str:
        """Get the currently selected remote file"""
        return self.selected_remote_file

    def ask_trust_host(self, host: str, fingerprint: str) -> bool:
        """Show a modal dialog asking user to trust an unknown host. Returns True if user clicks Yes."""
        result = {"trust": False}  # mutable container to get result

        def on_yes():
            result["trust"] = True
            dialog.destroy()

        def on_no():
            result["trust"] = False
            dialog.destroy()

        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Unknown Host Key")
        dialog.geometry("400x200")
        dialog.grab_set()  # makes it modal

        label = ctk.CTkLabel(
            dialog,
            text=f"Unknown host: {host}\nSHA256 fingerprint: {fingerprint}\n\nVerify this fingerprint with the server administrator before trusting.\nTrust this server and add to known_hosts?",
            wraplength=380
        )
        label.pack(padx=20, pady=20)

        btn_frame = ctk.CTkFrame(dialog)
        btn_frame.pack(pady=10)

        ctk.CTkButton(btn_frame, text="Yes", command=on_yes).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="No", command=on_no).pack(side="left", padx=10)

        dialog.wait_window()
        return result["trust"]

    def _on_view_local_file(self):
        """Handle View File button click"""
        if self.on_view_local_file_callback:
            self.on_view_local_file_callback()

    def _on_view_remote_file(self):
        """Handle View Remote File button click"""
        if self.on_view_remote_file_callback:
            self.on_view_remote_file_callback()

    def show_file_viewer(self, filename: str, content: str):
        """Display file content in a popup window"""
        viewer = ctk.CTkToplevel(self.root)
        viewer.title(f"View: {filename}")
        viewer.geometry("800x600")

        # Header with filename
        header = ctk.CTkFrame(viewer)
        header.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(header, text=f"File: {filename}", font=("Segoe UI", 12, "bold")).pack(anchor="w")

        # Content textbox
        content_text = ctk.CTkTextbox(viewer, font=("Consolas", 10), wrap="word")
        content_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        content_text.insert("0.0", content)
        content_text.configure(state="disabled")  # Read-only

        # Button frame
        btn_frame = ctk.CTkFrame(viewer)
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))

        def on_close():
            viewer.destroy()

        def on_copy():
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            self.log("Content copied to clipboard")

        ctk.CTkButton(btn_frame, text="Copy", command=on_copy).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Close", command=on_close).pack(side="left", padx=5)
