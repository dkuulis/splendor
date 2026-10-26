import tkinter as tk
from tkinter import ttk

from .card_panel import CardPanel
from .assets import load_image
from .styles import (
    GEM_SIZE,
    GEM_SPACING,
    MARKET_CARD_HEIGHT,
    MARKET_CARD_WIDTH,
    MUTED_TEXT_COLOR,
    PLAYER_CARD_OFFSET,
    PLAYER_PANEL_BACKGROUND,
    gem_centers,
)


class PlayerColumn(ttk.Frame):
    def __init__(self, parent, color, cards, gem_count):
        super().__init__(parent, style="Player.TFrame")
        stack_width = MARKET_CARD_WIDTH + max(0, len(cards) - 1) * PLAYER_CARD_OFFSET
        width = max(stack_width, GEM_SIZE + max(0, gem_count - 1) * GEM_SPACING)

        stack = tk.Canvas(self, width=width, height=MARKET_CARD_HEIGHT,
                          highlightthickness=0, borderwidth=0,
                          background=PLAYER_PANEL_BACKGROUND)
        stack.pack()
        self.images = []
        start = (width - stack_width) / 2
        for index, card in enumerate(cards):
            self.images.extend(CardPanel.draw(stack, card, x=start + index * PLAYER_CARD_OFFSET, owned=True))
        if not cards:
            stack.create_text(width / 2, MARKET_CARD_HEIGHT / 2,
                              text=color, fill=MUTED_TEXT_COLOR)

        if gem_count:
            self.gem_image = load_image(self, color.lower())
            for x in gem_centers(gem_count, width, GEM_SPACING):
                stack.create_image(x, MARKET_CARD_HEIGHT - GEM_SIZE / 2 - 5, image=self.gem_image)
