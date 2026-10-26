import tkinter as tk

from .styles import (
    DECK_LABEL_FONT,
    DECK_PALETTE,
    DECK_SYMBOL_FONT,
    DECK_TEXT_COLOR,
    MARKET_CARD_WIDTH,
    MARKET_CARD_HEIGHT,
)


class DeckPanel(tk.Canvas):
    def __init__(self, parent, tier, cards):
        super().__init__(parent, background=DECK_PALETTE[tier],
                         width=MARKET_CARD_WIDTH, height=MARKET_CARD_HEIGHT,
                         highlightthickness=0, borderwidth=0)

        center_x = MARKET_CARD_WIDTH / 2
        self.create_text(center_x, 24, text=f"LEVEL {tier}",
                         fill=DECK_TEXT_COLOR, font=DECK_LABEL_FONT)
        self.create_text(center_x, MARKET_CARD_HEIGHT / 2, text="◆" * tier,
                         fill=DECK_TEXT_COLOR, font=DECK_SYMBOL_FONT)
        self.create_text(center_x, MARKET_CARD_HEIGHT - 24, text=f"{len(cards)} cards",
                         fill=DECK_TEXT_COLOR, font="TkDefaultFont")
