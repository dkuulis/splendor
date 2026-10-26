import tkinter as tk

from .styles import (
    DECK_LABEL_FONT,
    DECK_PALETTE,
    DECK_SYMBOL_FONT,
    DECK_TEXT_COLOR,
)


class DeckPanel(tk.Frame):
    def __init__(self, parent, tier, cards):
        super().__init__(parent, bg=DECK_PALETTE[tier], padx=12, pady=12)

        tk.Label(self, text=f"LEVEL {tier}", bg=DECK_PALETTE[tier], fg=DECK_TEXT_COLOR, font=DECK_LABEL_FONT).pack()
        tk.Label(self, text="◆" * tier, bg=DECK_PALETTE[tier], fg=DECK_TEXT_COLOR, font=DECK_SYMBOL_FONT).pack(expand=True)
        tk.Label(self, text=f"{len(cards)} cards", bg=DECK_PALETTE[tier], fg=DECK_TEXT_COLOR).pack(pady=5)
