import tkinter as tk
from tkinter import ttk

from .drawing import draw_card_marker, draw_gem, row_centers
from .styles import MUTED_TEXT_COLOR, PLAYER_PANEL_BACKGROUND

MARKER_SIZE = 24
MARKER_GAP = 4
MARKER_SPACING = MARKER_SIZE + MARKER_GAP
INVENTORY_MIN_WIDTH = 100
INVENTORY_HEIGHT = 72
CARD_ROW_Y = 18
GEM_ROW_Y = 52


class PlayerColumn(ttk.Frame):
    def __init__(self, parent, color, card_count, gem_count):
        super().__init__(parent, style="Player.TFrame")
        content_width = max(card_count, gem_count) * MARKER_SPACING
        canvas_width = max(INVENTORY_MIN_WIDTH, content_width)

        resources = tk.Canvas(
            self, width=canvas_width, height=INVENTORY_HEIGHT, highlightthickness=0,
            background=PLAYER_PANEL_BACKGROUND,
        )
        resources.pack()

        for x in row_centers(card_count, canvas_width, MARKER_SPACING):
            draw_card_marker(resources, color, x, CARD_ROW_Y, MARKER_SIZE)
        for x in row_centers(gem_count, canvas_width, MARKER_SPACING):
            draw_gem(resources, color, x, GEM_ROW_Y, MARKER_SIZE / 2)
        ttk.Label(self, text=color, foreground=MUTED_TEXT_COLOR, style="Player.TLabel").pack()
