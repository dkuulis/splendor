import tkinter as tk
from tkinter import ttk

from .drawing import draw_card_marker, draw_gem, row_centers
from .styles import GEM_RADIUS, GEM_SPACING, MUTED_TEXT_COLOR, PLAYER_PANEL_BACKGROUND

MARKER_SIZE = GEM_RADIUS * 2
INVENTORY_MIN_WIDTH = 100
ROW_GAP = 10
CARD_ROW_Y = 6 + GEM_RADIUS
GEM_ROW_Y = CARD_ROW_Y + MARKER_SIZE + ROW_GAP
INVENTORY_HEIGHT = GEM_ROW_Y + GEM_RADIUS + 8


class PlayerColumn(ttk.Frame):
    def __init__(self, parent, color, card_count, gem_count):
        super().__init__(parent, style="Player.TFrame")
        content_width = max(card_count, gem_count) * GEM_SPACING
        canvas_width = max(INVENTORY_MIN_WIDTH, content_width)

        resources = tk.Canvas(
            self, width=canvas_width, height=INVENTORY_HEIGHT, highlightthickness=0,
            background=PLAYER_PANEL_BACKGROUND,
        )
        resources.pack()

        for x in row_centers(card_count, canvas_width, GEM_SPACING):
            draw_card_marker(resources, color, x, CARD_ROW_Y, MARKER_SIZE)
        for x in row_centers(gem_count, canvas_width, GEM_SPACING):
            draw_gem(resources, color, x, GEM_ROW_Y, GEM_RADIUS, width=2)
        ttk.Label(self, text=color, foreground=MUTED_TEXT_COLOR, style="Player.TLabel").pack()
