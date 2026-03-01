import customtkinter as ctk
from styles import *
import database as db

class SettingsView(ctk.CTkFrame):
    def __init__(self, master, manager, **kwargs):
        super().__init__(master, **kwargs)
        self.manager = manager
        self.configure(fg_color="transparent")
        
        self.setup_ui()

    def setup_ui(self):
        # Header
        self.header = ctk.CTkLabel(self, text="Settings", font=FONT_TITLE)
        self.header.pack(pady=(20, 10), padx=20, anchor="w")

        # Profile Frame
        self.profile_frame = ctk.CTkFrame(self, fg_color=COLOR_SIDEBAR, corner_radius=15)
        self.profile_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(self.profile_frame, text="User Profile", font=FONT_SUBTITLE).pack(pady=15, padx=20, anchor="w")
        
        user = db.get_user_profile()
        name = user[1] if user else "User"
        start_date = user[2] if user else ""
        
        # Name
        name_frame = ctk.CTkFrame(self.profile_frame, fg_color="transparent")
        name_frame.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(name_frame, text="Display Name:", font=FONT_BODY, width=120, anchor="w").pack(side="left")
        self.name_entry = ctk.CTkEntry(name_frame, border_color=COLOR_ACCENT)
        self.name_entry.insert(0, name)
        self.name_entry.pack(side="left", fill="x", expand=True)

        # Start Date (read only for now)
        date_frame = ctk.CTkFrame(self.profile_frame, fg_color="transparent")
        date_frame.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(date_frame, text="Start Date:", font=FONT_BODY, width=120, anchor="w").pack(side="left")
        self.date_label = ctk.CTkLabel(date_frame, text=start_date, font=FONT_BODY)
        self.date_label.pack(side="left")

        # Save Profile Button
        self.save_btn = ctk.CTkButton(self.profile_frame, text="Save Changes", fg_color=COLOR_ACCENT, hover_color="#304FFE", command=self.save_settings)
        self.save_btn.pack(pady=20, padx=20)

    def save_settings(self):
        # This is a bit simplified, but updates the name
        # A more robust version would allow changing the start date too
        print(f"Saving profile for {self.name_entry.get()}")
        # db.update_user_profile(self.name_entry.get())
        pass
