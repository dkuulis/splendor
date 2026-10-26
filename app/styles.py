"""Shared UI colors, fonts, dimensions, and theme configuration."""

from tkinter import ttk

CARD_BACKGROUND = "#ffffff"
DECK_PALETTE = {1: "#166534", 2: "#80601f", 3: "#1e40af"}
TABLE_BACKGROUND = "#a99b88"
TEXT_COLOR = "#30271f"
PLAYER_PANEL_BACKGROUND = TABLE_BACKGROUND
INACTIVE_PLAYER_BORDER = "#958570"

POINTS_FONT = ("Forum", -48, "bold")
SCORE_CENTER_X = 116

TOKEN_SIZE = 60
TOKEN_GAP = 5
TOKEN_SPACING = TOKEN_SIZE + TOKEN_GAP
TOKEN_PILE_WIDTH = 3 * TOKEN_SIZE + 4
TOKEN_PILE_HEIGHT = 2 * TOKEN_SIZE + 4

WINDOW_MIN_WIDTH = 1700

MARKET_CARD_WIDTH = 150
MARKET_CARD_HEIGHT = MARKET_CARD_WIDTH * 7 // 5
ACTION_BUTTON_WIDTH = 140
ACTION_BUTTON_HEIGHT = 120
RESTART_BUTTON_HEIGHT = 42
ACTION_BUTTON_TOPS = (0, MARKET_CARD_HEIGHT - RESTART_BUTTON_HEIGHT)
NOBLE_SIZE = 150
MARKET_ROW_PADDING = 4
PLAYER_CARD_OFFSET = 30
PLAYER_COLUMN_GAP = 12
TOKEN_OVERHANG = 20
PLAYER_PANEL_PADDING = 5


def configure_styles(root):
    style = ttk.Style(root)
    root.configure(background=TABLE_BACKGROUND)
    style.configure("TFrame", background=TABLE_BACKGROUND)
    style.configure("TLabel", background=TABLE_BACKGROUND, foreground=TEXT_COLOR)
    style.configure("Player.TFrame", background=PLAYER_PANEL_BACKGROUND)
    # Use only the image label to avoid platform-dependent native button padding.
    style.layout("Action.TButton", [("Button.label", {"sticky": "nswe"})])
    style.configure("Action.TButton", padding=0, borderwidth=0)
