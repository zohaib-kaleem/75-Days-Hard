import customtkinter as ctk
import database as db
from styles import *
from models import ChallengeManager
from views.dashboard import DashboardView
from views.analytics import AnalyticsView
from views.settings import SettingsView
from views.task_manager import TaskManagerView
from datetime import date
import os

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Window Setup
        self.title("75 Days Challenge Tracker")
        self.geometry("1100x700")
        set_appearance()
        
        # Init DB
        db.init_db()
        
        # Load User Profile
        user = db.get_user_profile()
        if not user:
            db.create_user_profile("Challenger", date.today().isoformat())
            user = db.get_user_profile()
            
        self.manager = ChallengeManager(user[2]) 
        
        # UI Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.setup_sidebar()
        self.show_home()

    def setup_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=COLOR_SIDEBAR)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="75 DAYS", font=FONT_TITLE, text_color=COLOR_ACCENT)
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.home_btn = ctk.CTkButton(self.sidebar_frame, text="Home (Tasks)", font=FONT_BODY, 
                                      fg_color="transparent", text_color=COLOR_TEXT, 
                                      anchor="w", command=self.show_home)
        self.home_btn.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.tracker_btn = ctk.CTkButton(self.sidebar_frame, text="Daily Tracker", font=FONT_BODY, 
                                      fg_color="transparent", text_color=COLOR_TEXT, 
                                      anchor="w", command=self.show_dashboard)
        self.tracker_btn.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.stats_btn = ctk.CTkButton(self.sidebar_frame, text="Analytics", font=FONT_BODY, 
                                       fg_color="transparent", text_color=COLOR_TEXT, 
                                       anchor="w", command=self.show_analytics)
        self.stats_btn.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        self.settings_btn = ctk.CTkButton(self.sidebar_frame, text="Settings", font=FONT_BODY, 
                                         fg_color="transparent", text_color=COLOR_TEXT, 
                                         anchor="w", command=self.show_settings)
        self.settings_btn.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Appearance Mode:", font=FONT_CAPTION)
        self.appearance_mode_label.grid(row=6, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Dark", "Light"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=7, column=0, padx=20, pady=(10, 20))

    def show_home(self):
        if hasattr(self, "current_view"):
            self.current_view.destroy()
        self.current_view = TaskManagerView(self)
        self.current_view.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

    def show_dashboard(self):
        if hasattr(self, "current_view"):
            self.current_view.destroy()
        self.current_view = DashboardView(self, self.manager)
        self.current_view.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

    def show_analytics(self):
        if hasattr(self, "current_view"):
            self.current_view.destroy()
        self.current_view = AnalyticsView(self, self.manager)
        self.current_view.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

    def show_settings(self):
        if hasattr(self, "current_view"):
            self.current_view.destroy()
        self.current_view = SettingsView(self, self.manager)
        self.current_view.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

    def refresh_analytics(self):
        if hasattr(self, "current_view") and isinstance(self.current_view, AnalyticsView):
            self.current_view.setup_ui()

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)
        # Refresh current view to update non-reactive elements like Canvas or Charts
        if hasattr(self, "current_view"):
            if isinstance(self.current_view, DashboardView):
                self.current_view.notebook.update_colors()
            elif isinstance(self.current_view, AnalyticsView):
                self.refresh_analytics()

if __name__ == "__main__":
    app = App()
    app.mainloop()
