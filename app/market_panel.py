from tkinter import ttk

from .card_panel import CardPanel
from .deck_panel import DeckPanel
from .styles import MARKET_ROW_PADDING, MARKET_CARD_WIDTH, MARKET_CARD_HEIGHT


class MarketPanel(ttk.Frame):
    def __init__(self, parent, market, on_select=None, can_buy=None, selected_card=None):
        super().__init__(parent)

        for row, tier in enumerate((3, 2, 1)):
            deck = DeckPanel(self, tier)
            deck.grid(row=row, column=0, padx=4, pady=MARKET_ROW_PADDING)

            for slot, card in enumerate(market[tier]):
                if card is selected_card:
                    panel = ttk.Frame(self, width=MARKET_CARD_WIDTH, height=MARKET_CARD_HEIGHT)
                else:
                    panel = CardPanel(self, card, on_select, can_buy(card) if can_buy else False)
                panel.grid(row=row, column=slot + 1, padx=4, pady=MARKET_ROW_PADDING)
