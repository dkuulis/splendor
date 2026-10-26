"""Shared UI colors, fonts, dimensions, and theme configuration."""

from tkinter import ttk

PALETTE = {"Diamond": "#e5e7eb", "Sapphire": "#2563eb", "Emerald": "#15803d", "Ruby": "#be123c", "Onyx": "#334155"}
TEXT_PALETTE = {"Diamond": "#111827", "Sapphire": "white", "Emerald": "white", "Ruby": "white", "Onyx": "white"}
OUTLINE_PALETTE = {**PALETTE, "Diamond": "#94a3b8"}
DISABLED_PALETTE = {"Diamond": "#c4c7cc", "Sapphire": "#899bbd", "Emerald": "#819e8b", "Ruby": "#b48590", "Onyx": "#858d99"}
DISABLED_CARD_BORDER = "#a3a3a3"
CARD_BACKGROUND = "#ffffff"
DECK_PALETTE = {1: "#166534", 2: "#a16207", 3: "#1e40af"}
MUTED_TEXT_COLOR = "#64748b"
LOG_BACKGROUND = "#f8fafc"
PLAYER_PANEL_BACKGROUND = "#f8fafc"
ACTIVE_PLAYER_BORDER = "#2563eb"
DECK_TEXT_COLOR = "white"
SELECTION_OUTLINE_COLOR = "#f59e0b"

TITLE_FONT = ("Helvetica", 24, "bold")
SUBTITLE_FONT = ("Helvetica", 12)
LOG_FONT = ("Helvetica", 11)
DECK_LABEL_FONT = ("Helvetica", 11, "bold")
DECK_SYMBOL_FONT = ("Helvetica", 16, "bold")
POINTS_FONT = ("Helvetica", 28, "bold")
CARD_DETAIL_FONT = ("Helvetica", 13, "bold")
SELECTION_MARKER_FONT = ("Helvetica", 20, "bold")

GEM_RADIUS = 19
GEM_GAP = 4
GEM_SPACING = GEM_RADIUS * 2 + GEM_GAP

MARKET_CARD_WIDTH = 150
MARKET_CARD_HEIGHT = MARKET_CARD_WIDTH * 7 // 5
CARD_BORDER_WIDTH = 2
PLAYER_CARD_OFFSET = 10
COST_GEM_RADIUS = 14
COST_GEM_SPACING = COST_GEM_RADIUS * 2 + 4


def configure_styles(root):
    style = ttk.Style(root)
    for name in ("Player.TLabelframe", "Player.TLabelframe.Label", "Player.TFrame", "Player.TLabel"):
        style.configure(name, background=PLAYER_PANEL_BACKGROUND)
