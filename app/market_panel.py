from tkinter import ttk

from .card_panel import CardPanel
from .deck_panel import DeckPanel


class MarketPanel(ttk.Frame):
    def __init__(self, parent, market, on_buy=None, can_buy=None):
        super().__init__(parent)

        for row, tier in enumerate((3, 2, 1)):
            deck = DeckPanel(self, tier)
            deck.grid(row=row, column=0, padx=4, pady=4)

            for slot, card in enumerate(market[tier]):
                panel = CardPanel(self, card, on_buy, can_buy(card) if can_buy else False)
                panel.grid(row=row, column=slot + 1, padx=4, pady=4)
