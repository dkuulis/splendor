import tkinter as tk
from .assets import load_image

from .styles import (
    DECK_PALETTE,
    MARKET_CARD_WIDTH,
    MARKET_CARD_HEIGHT,
)


class DeckPanel(tk.Canvas):
    def __init__(self, parent, tier):
        super().__init__(parent, background=DECK_PALETTE[tier],
                         width=MARKET_CARD_WIDTH, height=MARKET_CARD_HEIGHT,
                         highlightthickness=0, borderwidth=0)

        self.image = load_image(self, f"deck_level_{tier}")
        self.create_image(0, 0, image=self.image, anchor="nw")
