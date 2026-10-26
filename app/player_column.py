import tkinter as tk
from tkinter import ttk

from .card_panel import CardPanel
from .assets import load_image
from .styles import (
    GEM_SIZE,
    GEM_SPACING,
    MARKET_CARD_HEIGHT,
    MARKET_CARD_WIDTH,
    PLAYER_CARD_OFFSET,
    PLAYER_GEM_OVERHANG,
    PLAYER_GEMS_PER_COLUMN,
    PLAYER_PANEL_BACKGROUND,
)


class PlayerColumn(ttk.Frame):
    def __init__(self, parent, color, cards, gem_count):
        super().__init__(parent, style="Player.TFrame")
        stack_width = MARKET_CARD_WIDTH + max(0, len(cards) - 1) * PLAYER_CARD_OFFSET
        gem_columns = (gem_count + PLAYER_GEMS_PER_COLUMN - 1) // PLAYER_GEMS_PER_COLUMN
        gem_width = GEM_SIZE + max(0, gem_columns - 1) * GEM_SPACING if gem_count else 0
        overhang = PLAYER_GEM_OVERHANG if gem_count else 0
        width = max(stack_width + overhang, gem_width)

        stack = tk.Canvas(self, width=width, height=MARKET_CARD_HEIGHT,
                          highlightthickness=0, borderwidth=0,
                          background=PLAYER_PANEL_BACKGROUND)
        stack.pack()
        self.images = []
        # Keep the right card edge aligned with the rightmost gem column, while
        # allowing extra gem columns to extend left without clipping.
        start = width - overhang - stack_width
        for index, card in enumerate(cards):
            self.images.extend(CardPanel.draw(stack, card, x=start + index * PLAYER_CARD_OFFSET, owned=True))

        if gem_count:
            self.gem_image = load_image(self, color.lower())
            for index in range(gem_count):
                column, row = divmod(index, PLAYER_GEMS_PER_COLUMN)
                x = width - GEM_SIZE / 2 - column * GEM_SPACING
                y = MARKET_CARD_HEIGHT - GEM_SIZE / 2 - row * GEM_SPACING
                stack.create_image(x, y, image=self.gem_image)
