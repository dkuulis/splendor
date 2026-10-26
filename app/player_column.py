import tkinter as tk
from tkinter import ttk

from .card_panel import CardPanel
from .drawing import draw_gem, row_centers
from .styles import (
    GEM_RADIUS,
    GEM_SPACING,
    MARKET_CARD_HEIGHT,
    MARKET_CARD_WIDTH,
    MUTED_TEXT_COLOR,
    PLAYER_CARD_OFFSET,
    PLAYER_PANEL_BACKGROUND,
)


class PlayerColumn(ttk.Frame):
    def __init__(self, parent, color, cards, gem_count):
        super().__init__(parent, style="Player.TFrame")
        stack_width = MARKET_CARD_WIDTH + max(0, len(cards) - 1) * PLAYER_CARD_OFFSET
        width = max(stack_width, gem_count * GEM_SPACING)

        stack = tk.Canvas(self, width=width, height=MARKET_CARD_HEIGHT,
                          highlightthickness=0, borderwidth=0,
                          background=PLAYER_PANEL_BACKGROUND)
        stack.pack()
        start = (width - stack_width) / 2
        for index, card in enumerate(cards):
            CardPanel.draw(stack, card, x=start + index * PLAYER_CARD_OFFSET)
        if not cards:
            stack.create_text(width / 2, MARKET_CARD_HEIGHT / 2,
                              text=color, fill=MUTED_TEXT_COLOR)

        for x in row_centers(gem_count, width, GEM_SPACING):
            draw_gem(stack, color, x, MARKET_CARD_HEIGHT - GEM_RADIUS - 5,
                     GEM_RADIUS, width=2)
