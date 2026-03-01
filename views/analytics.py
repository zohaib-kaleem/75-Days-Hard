import customtkinter as ctk
from styles import *
import database as db
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta

class AnalyticsView(ctk.CTkFrame):
    def __init__(self, master, manager, **kwargs):
        super().__init__(master, **kwargs)
        self.manager = manager
        self.configure(fg_color="transparent")
        
        self.setup_ui()

    def setup_ui(self):
        # Clear existing widgets for live refresh
        for widget in self.winfo_children():
            widget.destroy()
            
        # Header
        self.header = ctk.CTkLabel(self, text="Progress Analytics (75 Hard Streak)", font=FONT_TITLE, text_color=COLOR_ACCENT)
        self.header.pack(pady=(20, 10), padx=20, anchor="w")

        # Stats Cards
        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.pack(fill="x", padx=20, pady=10)
        
        start_date_str = self.manager.start_date_str
        streak, streak_start, is_today_done = db.get_streak_info(start_date_str)
        
        self.create_stat_card(self.stats_frame, "Current Streak", f"{streak} Days", 0)
        self.create_stat_card(self.stats_frame, "Challenge Day", str(self.manager.get_current_day_number()), 1)
        
        status = "Complete" if is_today_done else "Incomplete"
        self.create_stat_card(self.stats_frame, "Today's Status", status, 2)

        # Charts Section
        self.charts_frame = ctk.CTkScrollableFrame(self, fg_color=COLOR_SIDEBAR, corner_radius=15)
        self.charts_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.plot_progress_chart(streak_start)

    def create_stat_card(self, master, title, value, col):
        card = ctk.CTkFrame(master, fg_color=COLOR_SIDEBAR, corner_radius=10, height=100)
        card.grid(row=0, column=col, padx=10, sticky="nsew")
        master.grid_columnconfigure(col, weight=1)
        
        ctk.CTkLabel(card, text=title, font=FONT_CAPTION, text_color=COLOR_TEXT_DIM).pack(pady=(15, 0))
        ctk.CTkLabel(card, text=value, font=FONT_SUBTITLE, text_color=COLOR_ACCENT).pack(pady=(0, 15))

    def plot_progress_chart(self, streak_start_str):
        # Get daily completion data since streak start
        data = db.get_daily_completion_data(streak_start_str)
        
        if not data:
            for widget in self.charts_frame.winfo_children():
                widget.destroy()
            label = ctk.CTkLabel(self.charts_frame, text="Start your streak today!", font=FONT_SUBTITLE, text_color=COLOR_TEXT_DIM)
            label.pack(expand=True, pady=50)
            return

        days = [f"Day {i+1}" for i in range(len(data))]
        labels = [row[0][5:] for row in data] # MM-DD
        percentages = [row[1] for row in data]
        
        appearance = ctk.get_appearance_mode()
        bg_color = COLOR_SIDEBAR[0] if appearance == "Light" else COLOR_SIDEBAR[1]
        text_color = COLOR_TEXT[0] if appearance == "Light" else COLOR_TEXT[1]
        
        for widget in self.charts_frame.winfo_children():
            widget.destroy()

        plt.rcParams.update({'font.family': 'Segoe Print'})
        fig, ax = plt.subplots(figsize=(8, 5), facecolor=bg_color)
        ax.set_facecolor(bg_color)
        
        # Bar Chart
        bars = ax.bar(days, percentages, color=COLOR_ACCENT, alpha=0.8)
        
        # Add thin line at 100%
        ax.axhline(y=100, color=COLOR_WARNING, linestyle='--', alpha=0.5, label="Target (100%)")
        
        ax.set_title(f"Streak Progress (Day 1 to Now)", color=text_color, fontsize=16, pad=20)
        ax.set_ylabel("Completion %", color=text_color)
        ax.tick_params(axis='x', colors=text_color, rotation=45)
        ax.tick_params(axis='y', colors=text_color)
        ax.set_ylim(0, 110)
        
        for spine in ax.spines.values():
            spine.set_edgecolor(text_color)
            spine.set_alpha(0.3)
            
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=self.charts_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        plt.close(fig)
