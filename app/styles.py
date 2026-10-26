"""Shared UI colors, fonts, dimensions, and theme configuration."""

from tkinter import ttk

CARD_BACKGROUND = "#ffffff"
DECK_PALETTE = {1: "#166534", 2: "#80601f", 3: "#1e40af"}
MUTED_TEXT_COLOR = "#64748b"
LOG_BACKGROUND = "#f8fafc"
PLAYER_PANEL_BACKGROUND = "#ffffff"
ACTIVE_PLAYER_BORDER = "#c5b58d"
INACTIVE_PLAYER_BORDER = "#e5e7eb"

LOG_FONT = ("Helvetica", 11)
POINTS_FONT = ("Forum", -48, "bold")

GEM_SIZE = 60
GEM_GAP = 5
GEM_SPACING = GEM_SIZE + GEM_GAP
BANK_PILE_WIDTH = 3 * GEM_SIZE + 4
BANK_PILE_HEIGHT = 2 * GEM_SIZE + 4

WINDOW_MIN_WIDTH = 1700

MARKET_CARD_WIDTH = 150
MARKET_CARD_HEIGHT = MARKET_CARD_WIDTH * 7 // 5
MARKET_ROW_PADDING = 4
PLAYER_CARD_OFFSET = 30
PLAYER_COLUMN_GAP = 12
PLAYER_GEM_OVERHANG = 20
PLAYER_GEMS_PER_COLUMN = 2
PLAYER_PANEL_PADDING = 5


def gem_centers(count, width, spacing):
    start = (width - (count - 1) * spacing) / 2
    return [start + index * spacing for index in range(count)]


def configure_styles(root):
    style = ttk.Style(root)
    for name in ("Player.TFrame", "Player.TLabel"):
        style.configure(name, background=PLAYER_PANEL_BACKGROUND)
