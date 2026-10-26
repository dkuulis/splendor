from tkinter import ttk

from .card_panel import CardPanel
from .deck_panel import DeckPanel


class MarketPanel(ttk.Frame):
    def __init__(self, parent, market, decks, on_buy=None, can_buy=None):
        super().__init__(parent)
        self.deck_panels = {}
        self.card_panels = {}

        for row, tier in enumerate((3, 2, 1)):
            self.rowconfigure(row, weight=1, uniform="rows")
            deck = DeckPanel(self, tier, decks[tier])
            deck.grid(row=row, column=0, sticky="nsew", padx=(0, 8), pady=4)
            self.deck_panels[tier] = deck
            self.card_panels[tier] = []

            for slot, card in enumerate(market[tier]):
                self.columnconfigure(slot + 1, weight=1, uniform="cards")
                panel = CardPanel(self, card, on_buy, can_buy(card) if can_buy else False)
                panel.grid(row=row, column=slot + 1, sticky="nsew", padx=4, pady=4)
                self.card_panels[tier].append(panel)
