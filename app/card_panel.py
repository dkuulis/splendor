import tkinter as tk
from .assets import load_image

from .styles import CARD_BACKGROUND, MARKET_CARD_WIDTH, MARKET_CARD_HEIGHT


class CardPanel(tk.Canvas):
    def __init__(self, parent, card=None, on_select=None, affordable=False, owned=False):
        super().__init__(parent, width=MARKET_CARD_WIDTH, height=MARKET_CARD_HEIGHT,
                         highlightthickness=0, borderwidth=0, background=CARD_BACKGROUND)
        self.on_select = on_select
        self.art = self.create_image(0, 0, anchor="nw")
        self.overlay = self.create_image(0, 0, anchor="nw", image=load_image(self, "disabled"))
        self.bind("<Button-1>", self.select)
        self.refresh(card, affordable, owned)

    def refresh(self, card, affordable=False, owned=False):
        self.card = card
        self.enabled = bool(card and self.on_select and affordable and not owned)
        self.configure(cursor="hand2" if self.enabled else "")
        self.itemconfigure(self.art, image=load_image(self, card.id) if card else "")
        self.itemconfigure(self.overlay, state="normal" if card and not self.enabled and not owned else "hidden")

    def select(self, event):
        if self.enabled:
            self.on_select(self.card)
