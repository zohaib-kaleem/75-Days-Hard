import customtkinter as ctk

# Color Palette (Theme-Aware)
COLOR_BACKGROUND = ("#F5F5F5", "#121212")
COLOR_SIDEBAR = ("#E0E0E0", "#1E1E1E")
COLOR_ACCENT = "#3D5AFE"
COLOR_SUCCESS = "#00C853"
COLOR_WARNING = "#FFD600"
COLOR_TEXT = ("#212121", "#E0E0E0")
COLOR_TEXT_DIM = ("#757575", "#9E9E9E")

# Notebook Theme Colors
COLOR_PAPER_LIGHT = "#FFF9E5" # Vintage white/yellow
COLOR_PAPER_DARK = "#2C2C2C"  # Dark gray
COLOR_PAPER_LINE = ("#B3E5FC", "#424242") # Light blue in light mode, gray in dark
COLOR_PAPER_MARGIN = ("#FFCDD2", "#5E3535") # Light red in light mode, dark red in dark

# Font Settings
# We use "Segoe Print" as a default notebook font on Windows.
FONT_TITLE = ("Segoe Print", 28, "bold")
FONT_SUBTITLE = ("Segoe Print", 20, "bold")
FONT_HANDWRITTEN = ("Segoe Print", 14)
FONT_HANDWRITTEN_STRIKE = ("Segoe Print", 14, "overstrike")
FONT_BODY = ("Inter", 14)
FONT_CAPTION = ("Inter", 12)

def set_appearance():
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
