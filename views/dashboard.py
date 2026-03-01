import customtkinter as ctk
from styles import *
import database as db
from datetime import date
from views.notebook import NotebookFrame

class DashboardView(ctk.CTkFrame):
    def __init__(self, master, manager, **kwargs):
        super().__init__(master, **kwargs)
        self.manager = manager
        self.configure(fg_color="transparent")
        
        # Notebook Background
        self.notebook = NotebookFrame(self)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Content Container (Scrollable)
        self.content = ctk.CTkScrollableFrame(self.notebook, fg_color="transparent")
        self.content.place(relx=0.08, rely=0.05, relwidth=0.9, relheight=0.9)
        
        self.setup_ui()
        self.load_today_state()

    def setup_ui(self):
        # Header
        current_day = self.manager.get_current_day_number()
        self.header = ctk.CTkLabel(self.content, text=f"Day {current_day}", 
                                   font=FONT_TITLE, text_color=COLOR_ACCENT)
        self.header.pack(pady=(10, 5), anchor="w")

        # Streak Reset Warning
        streak, streak_start, _ = db.get_streak_info(self.manager.start_date_str)
        if current_day == 1 and streak_start != self.manager.start_date_str:
            self.reset_label = ctk.CTkLabel(self.content, text="⚠️ STREAK RESET TO DAY 1 (Missed Task)", 
                                            font=FONT_BODY, text_color="#F44336")
            self.reset_label.pack(pady=(0, 10), anchor="w")

        # Progress bar (styled for notebook)
        self.progress_bar = ctk.CTkProgressBar(self.content, orientation="horizontal", height=10)
        self.progress_bar.set(self.manager.get_progress_percentage() / 100)
        self.progress_bar.pack(fill="x", pady=(0, 20))

        # Dynamic Sections
        self.sections_frames = {}
        self.checkboxes = {}
        
        sections = db.get_sections()
        for section in sections:
            sec_id, sec_name = section
            sec_frame = ctk.CTkFrame(self.content, fg_color="transparent")
            sec_frame.pack(fill="x", pady=10)
            
            ctk.CTkLabel(sec_frame, text=sec_name, font=FONT_SUBTITLE, text_color=COLOR_TEXT).pack(anchor="w")
            
            tasks = db.get_tasks_for_section(sec_id)
            for task in tasks:
                tid, tlabel, _, _ = task
                cb = ctk.CTkCheckBox(sec_frame, text=tlabel, font=FONT_HANDWRITTEN,
                                     command=lambda t=tid: self.toggle_task(t),
                                     hover_color=COLOR_ACCENT, border_color=COLOR_ACCENT)
                cb.pack(pady=5, padx=20, anchor="w")
                self.checkboxes[tid] = cb

    def load_today_state(self):
        today_str = date.today().isoformat()
        completions = db.get_completions_for_date(today_str)
        for tid, cb in self.checkboxes.items():
            if tid in completions and completions[tid] == 1:
                cb.select()
                cb.configure(font=FONT_HANDWRITTEN_STRIKE)
            else:
                cb.deselect()
                cb.configure(font=FONT_HANDWRITTEN)

    def toggle_task(self, task_id):
        cb = self.checkboxes[task_id]
        is_done = 1 if cb.get() else 0
        today_str = date.today().isoformat()
        db.save_task_completion(today_str, task_id, is_done)
        
        # Update Font (Strikethrough)
        if is_done:
            cb.configure(font=FONT_HANDWRITTEN_STRIKE)
        else:
            cb.configure(font=FONT_HANDWRITTEN)

        # Notify master to refresh analytics if it's the current view
        if hasattr(self.master, "refresh_analytics"):
            self.master.refresh_analytics()
