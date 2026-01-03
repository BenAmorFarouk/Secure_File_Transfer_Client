import customtkinter as ctk

def log_to_widget(widget: ctk.CTkTextbox, msg: str):
    widget.configure(state="normal")
    widget.insert("end", msg + "\n")
    widget.see("end")
    widget.configure(state="disabled")