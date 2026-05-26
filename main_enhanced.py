import customtkinter as ctk
import threading
import os
from pathlib import Path
from local_fs import LocalFileSystem
from remote_sftp import RemoteSFTP
from utils import log_to_widget


class SFTPApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Secure SFTP Client")
        self.root.geometry("1200x700")

        self.local_fs = LocalFileSystem()
        self.remote_sftp = RemoteSFTP()
        self.remote_sftp.log_callback = self._log_message
        self.remote_sftp.ask_trust_callback = self._ask_trust_host

        self.local_file_names = []
        self.remote_file_names = []
        self.trust_event = threading.Event()
        self.trust_result = False

        self._setup_ui()
        self._refresh_local()

    def _setup_ui(self):
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        top_frame = ctk.CTkFrame(main_frame)
        top_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(top_frame, text="Host:").pack(side="left", padx=5)
        self.host_entry = ctk.CTkEntry(top_frame, width=150)
        self.host_entry.pack(side="left", padx=5)
        self.host_entry.insert(0, "localhost")

        ctk.CTkLabel(top_frame, text="Port:").pack(side="left", padx=5)
        self.port_entry = ctk.CTkEntry(top_frame, width=80)
        self.port_entry.pack(side="left", padx=5)
        self.port_entry.insert(0, "22")

        ctk.CTkLabel(top_frame, text="User:").pack(side="left", padx=5)
        self.user_entry = ctk.CTkEntry(top_frame, width=100)
        self.user_entry.pack(side="left", padx=5)

        ctk.CTkLabel(top_frame, text="Password:").pack(side="left", padx=5)
        self.pass_entry = ctk.CTkEntry(top_frame, width=100, show="*")
        self.pass_entry.pack(side="left", padx=5)

        self.connect_btn = ctk.CTkButton(top_frame, text="Connect", command=self._connect)
        self.connect_btn.pack(side="left", padx=5)

        self.disconnect_btn = ctk.CTkButton(top_frame, text="Disconnect", command=self._disconnect, state="disabled")
        self.disconnect_btn.pack(side="left", padx=5)

        content_frame = ctk.CTkFrame(main_frame)
        content_frame.pack(fill="both", expand=True)

        left_frame = ctk.CTkFrame(content_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        ctk.CTkLabel(left_frame, text="Local Files", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 5))

        local_path_frame = ctk.CTkFrame(left_frame)
        local_path_frame.pack(fill="x", pady=(0, 5))
        self.local_path_label = ctk.CTkLabel(local_path_frame, text=self.local_fs.get_full_path(), text_color="gray")
        self.local_path_label.pack(anchor="w")

        local_buttons_frame = ctk.CTkFrame(left_frame)
        local_buttons_frame.pack(fill="x", pady=(0, 5))
        ctk.CTkButton(local_buttons_frame, text="Refresh", command=self._refresh_local).pack(side="left", padx=2)
        ctk.CTkButton(local_buttons_frame, text="Preview", command=self._preview_local).pack(side="left", padx=2)
        ctk.CTkButton(local_buttons_frame, text="Upload", command=self._upload_file).pack(side="left", padx=2)

        self.local_folders_listbox = ctk.CTkTextbox(left_frame, height=10)
        self.local_folders_listbox.pack(fill="both", expand=True, pady=(0, 5))
        self.local_folders_listbox.bind("<Double-Button-1>", self._on_local_folder_double_click)
        self.local_folders_listbox.bind("<Motion>", self._on_local_folders_motion)
        self.local_folders_listbox.bind("<Button-1>", lambda e: "break")
        self.local_folders_listbox.bind("<B1-Motion>", lambda e: "break")

        ctk.CTkLabel(left_frame, text="Files", font=("Arial", 10, "bold")).pack(anchor="w", pady=(5, 0))
        self.local_files_listbox = ctk.CTkTextbox(left_frame, height=8)
        self.local_files_listbox.pack(fill="both", expand=True)
        self.local_files_listbox.bind("<Button-1>", self._on_local_file_click)

        right_frame = ctk.CTkFrame(content_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

        ctk.CTkLabel(right_frame, text="Remote Files", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 5))

        remote_path_frame = ctk.CTkFrame(right_frame)
        remote_path_frame.pack(fill="x", pady=(0, 5))
        self.remote_path_label = ctk.CTkLabel(remote_path_frame, text="/", text_color="gray")
        self.remote_path_label.pack(anchor="w")

        remote_buttons_frame = ctk.CTkFrame(right_frame)
        remote_buttons_frame.pack(fill="x", pady=(0, 5))
        ctk.CTkButton(remote_buttons_frame, text="Refresh", command=self._refresh_remote).pack(side="left", padx=2)
        ctk.CTkButton(remote_buttons_frame, text="Preview", command=self._preview_remote).pack(side="left", padx=2)
        ctk.CTkButton(remote_buttons_frame, text="Download", command=self._download_file).pack(side="left", padx=2)

        self.remote_folders_listbox = ctk.CTkTextbox(right_frame, height=10)
        self.remote_folders_listbox.pack(fill="both", expand=True, pady=(0, 5))
        self.remote_folders_listbox.bind("<Double-Button-1>", self._on_remote_folder_double_click)
        self.remote_folders_listbox.bind("<Motion>", self._on_remote_folders_motion)
        self.remote_folders_listbox.bind("<Button-1>", lambda e: "break")
        self.remote_folders_listbox.bind("<B1-Motion>", lambda e: "break")

        ctk.CTkLabel(right_frame, text="Files", font=("Arial", 10, "bold")).pack(anchor="w", pady=(5, 0))
        self.remote_files_listbox = ctk.CTkTextbox(right_frame, height=8)
        self.remote_files_listbox.pack(fill="both", expand=True)
        self.remote_files_listbox.bind("<Button-1>", self._on_remote_file_click)

        log_frame = ctk.CTkFrame(main_frame)
        log_frame.pack(fill="both", expand=True, pady=(10, 0))

        ctk.CTkLabel(log_frame, text="Log", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
        self.log_textbox = ctk.CTkTextbox(log_frame, height=6)
        self.log_textbox.pack(fill="both", expand=True)
        self.log_textbox.configure(state="disabled")

    def _refresh_local(self):
        self.local_path_label.configure(text=self.local_fs.get_full_path())

        self.local_folders_listbox.configure(state="normal")
        self.local_folders_listbox.delete("1.0", "end")
        for folder in self.local_fs.get_folders():
            self.local_folders_listbox.insert("end", f"📁 {folder}\n")
        self.local_folders_listbox.configure(state="disabled")

        self.local_files_listbox.configure(state="normal")
        self.local_files_listbox.delete("1.0", "end")
        self.local_file_names = []
        for filename, size in self.local_fs.get_files():
            self.local_file_names.append(filename)
            self.local_files_listbox.insert("end", f"📄 {filename} ({size} bytes)\n")
        self.local_files_listbox.configure(state="disabled")

    def _refresh_remote(self):
        if not self.remote_sftp.is_connected():
            self._log_message("Not connected to remote server")
            return

        self.remote_path_label.configure(text=self.remote_sftp.current_path)

        self.remote_folders_listbox.configure(state="normal")
        self.remote_folders_listbox.delete("1.0", "end")
        for folder in self.remote_sftp.get_folders():
            self.remote_folders_listbox.insert("end", f"📁 {folder}\n")
        self.remote_folders_listbox.configure(state="disabled")

        self.remote_files_listbox.configure(state="normal")
        self.remote_files_listbox.delete("1.0", "end")
        self.remote_file_names = []
        for filename, size in self.remote_sftp.get_files():
            self.remote_file_names.append(filename)
            self.remote_files_listbox.insert("end", f"📄 {filename} ({size} bytes)\n")
        self.remote_files_listbox.configure(state="disabled")

    def _on_local_folder_double_click(self, event):
        try:
            text_widget = event.widget
            index = text_widget.index(f"@{event.x},{event.y}")
            line_start = f"{index.split('.')[0]}.0"
            line_end = f"{index.split('.')[0]}.end"
            folder_text = text_widget.get(line_start, line_end).strip()
            folder_name = folder_text.replace("📁 ", "").strip()

            if self.local_fs.navigate_to(folder_name):
                self._refresh_local()
            else:
                self._log_message(f"Cannot navigate to {folder_name}")
        except Exception as e:
            self._log_message(f"Error: {str(e)}")

    def _on_local_folders_motion(self, event):
        try:
            event.widget.config(cursor="hand2")
        except:
            pass

    def _on_remote_folder_double_click(self, event):
        try:
            text_widget = event.widget
            index = text_widget.index(f"@{event.x},{event.y}")
            line_start = f"{index.split('.')[0]}.0"
            line_end = f"{index.split('.')[0]}.end"
            folder_text = text_widget.get(line_start, line_end).strip()
            folder_name = folder_text.replace("📁 ", "").strip()

            if self.remote_sftp.navigate_to(folder_name):
                self._refresh_remote()
            else:
                self._log_message(f"Cannot navigate to {folder_name}")
        except Exception as e:
            self._log_message(f"Error: {str(e)}")

    def _on_remote_folders_motion(self, event):
        try:
            event.widget.config(cursor="hand2")
        except:
            pass

    def _on_local_file_click(self, event):
        text_widget = event.widget
        index = text_widget.index(f"@{event.x},{event.y}")
        line_num = index.split(".")[0]
        line_start = f"{line_num}.0"
        line_end = f"{line_num}.end"
        text_widget.tag_remove("sel", "1.0", "end")
        text_widget.tag_add("sel", line_start, line_end)
        return "break"

    def _on_remote_file_click(self, event):
        text_widget = event.widget
        index = text_widget.index(f"@{event.x},{event.y}")
        line_num = index.split(".")[0]
        line_start = f"{line_num}.0"
        line_end = f"{line_num}.end"
        text_widget.tag_remove("sel", "1.0", "end")
        text_widget.tag_add("sel", line_start, line_end)
        return "break"

    def _connect(self):
        host = self.host_entry.get().strip()
        try:
            port = int(self.port_entry.get().strip())
        except ValueError:
            self._log_message("Invalid port number")
            return

        if not (1 <= port <= 65535):
            self._log_message("Port must be between 1 and 65535")
            return

        username = self.user_entry.get().strip()
        password_str = self.pass_entry.get()
        self.pass_entry.delete(0, "end")

        if not host or not username:
            self._log_message("Host and username are required")
            return

        password_bytes = bytearray(password_str.encode('utf-8')) if password_str else bytearray()

        def connect_thread():
            try:
                if self.remote_sftp.connect(host, port, username, password_str if password_str else None):
                    self.root.after(0, lambda: self.connect_btn.configure(state="disabled"))
                    self.root.after(0, lambda: self.disconnect_btn.configure(state="normal"))
                    self.root.after(0, lambda: self._refresh_remote())
                else:
                    self.root.after(0, lambda: self._log_message("Connection failed"))
            finally:
                password_bytes[:] = bytearray(len(password_bytes))

        thread = threading.Thread(target=connect_thread, daemon=True)
        thread.start()

    def _disconnect(self):
        self.remote_sftp.disconnect()
        self.connect_btn.configure(state="normal")
        self.disconnect_btn.configure(state="disabled")
        self.remote_folders_listbox.configure(state="normal")
        self.remote_folders_listbox.delete("1.0", "end")
        self.remote_folders_listbox.configure(state="disabled")
        self.remote_files_listbox.configure(state="normal")
        self.remote_files_listbox.delete("1.0", "end")
        self.remote_files_listbox.configure(state="disabled")
        self._log_message("Disconnected from remote server")

    def _preview_local(self):
        try:
            text_widget = self.local_files_listbox
            sel = text_widget.tag_ranges("sel")
            if sel:
                start, end = sel[0], sel[1]
                line_num = int(start.split(".")[0]) - 1
                if 0 <= line_num < len(self.local_file_names):
                    filename = self.local_file_names[line_num]
                    content = self.local_fs.read_file_content(filename)
                    self._show_preview(filename, content)
                else:
                    self._log_message("Invalid file selection")
            else:
                self._log_message("Select a file to preview")
        except Exception as e:
            self._log_message(f"Error: {str(e)}")

    def _preview_remote(self):
        if not self.remote_sftp.is_connected():
            self._log_message("Not connected to remote server")
            return

        try:
            text_widget = self.remote_files_listbox
            sel = text_widget.tag_ranges("sel")
            if sel:
                start, end = sel[0], sel[1]
                line_num = int(start.split(".")[0]) - 1
                if 0 <= line_num < len(self.remote_file_names):
                    filename = self.remote_file_names[line_num]
                    content = self.remote_sftp.read_file_content(filename)
                    self._show_preview(filename, content)
                else:
                    self._log_message("Invalid file selection")
            else:
                self._log_message("Select a file to preview")
        except Exception as e:
            self._log_message(f"Error: {str(e)}")

    def _show_preview(self, filename, content):
        preview_window = ctk.CTkToplevel(self.root)
        preview_window.title(f"Preview: {filename}")
        preview_window.geometry("600x400")

        text_widget = ctk.CTkTextbox(preview_window)
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        text_widget.insert("1.0", content)
        text_widget.configure(state="disabled")

    def _upload_file(self):
        if not self.remote_sftp.is_connected():
            self._log_message("Not connected to remote server")
            return

        try:
            text_widget = self.local_files_listbox
            sel = text_widget.tag_ranges("sel")
            if sel:
                start, end = sel[0], sel[1]
                line_num = int(start.split(".")[0]) - 1
                if not (0 <= line_num < len(self.local_file_names)):
                    self._log_message("Invalid file selection")
                    return

                filename = self.local_file_names[line_num]
                local_path = self.local_fs.get_selected_file(filename)

                if local_path:
                    def upload_thread():
                        if self.remote_sftp.upload_file(local_path, filename):
                            self.root.after(0, lambda: self._log_message(f"Uploaded {filename}"))
                            self.root.after(0, lambda: self._refresh_remote())
                        else:
                            self.root.after(0, lambda: self._log_message(f"Failed to upload {filename}"))

                    thread = threading.Thread(target=upload_thread, daemon=True)
                    thread.start()
                else:
                    self._log_message(f"Cannot find file {filename}")
            else:
                self._log_message("Select a file to upload")
        except Exception as e:
            self._log_message(f"Error: {str(e)}")

    def _download_file(self):
        if not self.remote_sftp.is_connected():
            self._log_message("Not connected to remote server")
            return

        try:
            text_widget = self.remote_files_listbox
            sel = text_widget.tag_ranges("sel")
            if sel:
                start, end = sel[0], sel[1]
                line_num = int(start.split(".")[0]) - 1
                if not (0 <= line_num < len(self.remote_file_names)):
                    self._log_message("Invalid file selection")
                    return

                filename = self.remote_file_names[line_num]
                local_dir = Path(self.local_fs.get_full_path()).resolve()
                local_path = (local_dir / filename).resolve()

                if not str(local_path).startswith(str(local_dir)):
                    self._log_message("Security error: path traversal detected")
                    return

                def download_thread():
                    if self.remote_sftp.download_file(filename, str(local_path)):
                        self.root.after(0, lambda: self._log_message(f"Downloaded {filename}"))
                        self.root.after(0, lambda: self._refresh_local())
                    else:
                        self.root.after(0, lambda: self._log_message(f"Failed to download {filename}"))

                thread = threading.Thread(target=download_thread, daemon=True)
                thread.start()
            else:
                self._log_message("Select a file to download")
        except Exception as e:
            self._log_message(f"Error: {str(e)}")

    def _log_message(self, message):
        log_to_widget(self.log_textbox, message)

    def _ask_trust_host(self, host, fingerprint):
        self.trust_result = False
        self.trust_event.clear()

        def show_trust_dialog():
            trust_window = ctk.CTkToplevel(self.root)
            trust_window.title("Trust Host?")
            trust_window.geometry("500x200")

            ctk.CTkLabel(trust_window, text=f"Unknown host: {host}", font=("Arial", 12, "bold")).pack(pady=10)
            ctk.CTkLabel(trust_window, text=f"SHA256: {fingerprint}", wraplength=450).pack(pady=10)

            def on_trust():
                self.trust_result = True
                trust_window.destroy()
                self.trust_event.set()

            def on_reject():
                trust_window.destroy()
                self.trust_event.set()

            button_frame = ctk.CTkFrame(trust_window)
            button_frame.pack(pady=10)

            ctk.CTkButton(button_frame, text="Trust", command=on_trust).pack(side="left", padx=5)
            ctk.CTkButton(button_frame, text="Reject", command=on_reject).pack(side="left", padx=5)

        self.root.after(0, show_trust_dialog)
        self.trust_event.wait()
        return self.trust_result

    def run(self):
        self.root.mainloop()
