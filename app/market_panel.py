from tkinter import ttk

from .card_panel import CardPanel
from .deck_panel import DeckPanel
from .styles import MARKET_ROW_PADDING, MARKET_CARD_WIDTH, MARKET_CARD_HEIGHT


class MarketPanel(ttk.Frame):
    def __init__(self, parent, market, on_select=None, can_buy=None, selected_card=None):
        super().__init__(parent)
        self.cards = []
        self.slots = {}
        self.can_buy = can_buy

        for row, tier in enumerate((3, 2, 1)):
            deck = DeckPanel(self, tier)
            deck.grid(row=row, column=0, padx=4, pady=MARKET_ROW_PADDING)

            self.slots[tier] = []
            for slot in range(4):
                space = ttk.Frame(self, width=MARKET_CARD_WIDTH, height=MARKET_CARD_HEIGHT)
                space.grid_propagate(False)
                space.grid(row=row, column=slot + 1, padx=4, pady=MARKET_ROW_PADDING)
                panel = CardPanel(space, on_buy=on_select)
                panel.grid(row=0, column=0)
                self.slots[tier].append(panel)
        self.refresh(market, selected_card)

    def refresh(self, market, selected_card=None):
        self.cards = []
        for tier, panels in self.slots.items():
            for slot, panel in enumerate(panels):
                card = market[tier][slot] if slot < len(market[tier]) else None
                panel.refresh(card, self.can_buy(card) if card and self.can_buy else False)
                self.cards.append((card, panel))
        self.refresh_selection(selected_card)

    def refresh_selection(self, selected_card):
        for card, panel in self.cards:
            if card is None or card is selected_card:
                # Keep the slot's size while the card appears in the selection panel.
                panel.grid_remove()
            else:
                panel.grid()
