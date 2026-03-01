import customtkinter as ctk
from styles import *
import database as db

class TaskManagerView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")
        
        self.setup_ui()

    def setup_ui(self):
        # Header
        self.header = ctk.CTkLabel(self, text="Task Management", font=FONT_TITLE, text_color=COLOR_ACCENT)
        self.header.pack(pady=(20, 10), padx=20, anchor="w")

        # Add Task Section
        self.add_frame = ctk.CTkFrame(self, fg_color=COLOR_SIDEBAR, corner_radius=15)
        self.add_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(self.add_frame, text="Add New Task", font=FONT_SUBTITLE).grid(row=0, column=0, columnspan=2, pady=10, padx=20, sticky="w")
        
        self.task_entry = ctk.CTkEntry(self.add_frame, placeholder_text="Task Label", width=300)
        self.task_entry.grid(row=1, column=0, padx=20, pady=10)
        
        self.section_entry = ctk.CTkEntry(self.add_frame, placeholder_text="Section (e.g. Health, Work)", width=200)
        self.section_entry.grid(row=1, column=1, padx=20, pady=10)
        
        self.add_btn = ctk.CTkButton(self.add_frame, text="Add Task", command=self.add_task_action)
        self.add_btn.grid(row=1, column=2, padx=20, pady=10)

        # Task List Section
        self.list_label = ctk.CTkLabel(self, text="Existing Tasks", font=FONT_SUBTITLE)
        self.list_label.pack(pady=(20, 5), padx=20, anchor="w")
        
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color=COLOR_SIDEBAR, corner_radius=15)
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.refresh_task_list()

    def refresh_task_list(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
            
        sections = db.get_sections()
        for section in sections:
            sid, sname = section
            ctk.CTkLabel(self.scroll_frame, text=sname, font=FONT_SUBTITLE, text_color=COLOR_ACCENT).pack(anchor="w", pady=(10, 5), padx=10)
            
            tasks = db.get_tasks_for_section(sid)
            for task in tasks:
                tid, tlabel, _, _ = task
                item_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
                item_frame.pack(fill="x", padx=20)
                
                ctk.CTkLabel(item_frame, text=tlabel, font=FONT_BODY).pack(side="left")
                
                remove_btn = ctk.CTkButton(item_frame, text="Remove", width=60, height=20, 
                                           fg_color="#F44336", hover_color="#D32F2F",
                                           command=lambda id=tid: self.remove_task_action(id))
                remove_btn.pack(side="right", padx=10)

    def add_task_action(self):
        label = self.task_entry.get()
        section = self.section_entry.get() or "General"
        if label:
            db.add_task(label, section)
            self.task_entry.delete(0, "end")
            self.refresh_task_list()

    def remove_task_action(self, task_id):
        db.remove_task(task_id)
        self.refresh_task_list()
