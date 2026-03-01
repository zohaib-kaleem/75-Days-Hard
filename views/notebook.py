import customtkinter as ctk
from styles import *

class NotebookFrame(ctk.CTkCanvas):
    def __init__(self, master, **kwargs):
        # We use a Canvas to draw the lines
        super().__init__(master, highlightthickness=0, **kwargs)
        self.bind("<Configure>", self.draw_lines)
        self.update_colors()

    def update_colors(self):
        appearance = ctk.get_appearance_mode()
        self.bg_color = COLOR_PAPER_LIGHT if appearance == "Light" else COLOR_PAPER_DARK
        
        # Extract correct hex from tuples for tkinter Canvas
        self.line_color = COLOR_PAPER_LINE[0] if appearance == "Light" else COLOR_PAPER_LINE[1]
        self.margin_color = COLOR_PAPER_MARGIN[0] if appearance == "Light" else COLOR_PAPER_MARGIN[1]
        
        self.configure(bg=self.bg_color)
        self.draw_lines()

    def draw_lines(self, event=None):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        
        # Draw Horizontal Lines
        line_spacing = 30
        for y in range(line_spacing, h, line_spacing):
            self.create_line(0, y, w, y, fill=self.line_color, width=1)
            
        # Draw Vertical Margin Line
        margin_x = 60
        self.create_line(margin_x, 0, margin_x, h, fill=self.margin_color, width=2)
