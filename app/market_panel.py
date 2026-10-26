import tkinter as tk
from tkinter import ttk

from .assets import load_image
from .card_panel import CardPanel
from .styles import DECK_PALETTE, MARKET_ROW_PADDING, MARKET_CARD_WIDTH, MARKET_CARD_HEIGHT


class MarketPanel(ttk.Frame):
    def __init__(self, parent, market, decks, on_select, can_buy, selected_card):
        super().__init__(parent)
        self.cards = []
        self.slots = {}
        self.decks = {}
        self.can_buy = can_buy
        self.columnconfigure(0, minsize=MARKET_CARD_WIDTH + 8)

        for row, tier in enumerate((3, 2, 1)):
            deck = tk.Canvas(self, background=DECK_PALETTE[tier],
                             width=MARKET_CARD_WIDTH, height=MARKET_CARD_HEIGHT,
                             highlightthickness=0, borderwidth=0)
            deck.create_image(0, 0, image=load_image(deck, f"deck_level_{tier}"), anchor="nw")
            deck.grid(row=row, column=0, padx=4, pady=MARKET_ROW_PADDING)
            self.decks[tier] = deck

            self.slots[tier] = []
            for slot in range(4):
                space = ttk.Frame(self, width=MARKET_CARD_WIDTH, height=MARKET_CARD_HEIGHT)
                space.grid_propagate(False)
                space.grid(row=row, column=slot + 1, padx=4, pady=MARKET_ROW_PADDING)
                panel = CardPanel(space, on_select=on_select)
                panel.grid(row=0, column=0)
                self.slots[tier].append(panel)
        self.refresh(market, decks, selected_card)

    def refresh(self, market, decks, selected_card):
        self.cards = []
        for tier, deck in self.decks.items():
            if decks[tier]:
                deck.grid()
            else:
                deck.grid_remove()
        for tier, panels in self.slots.items():
            for slot, panel in enumerate(panels):
                card = market[tier][slot] if slot < len(market[tier]) else None
                panel.refresh(card, self.can_buy(card) if card else False)
                self.cards.append((card, panel))
        self.refresh_selection(selected_card)

    def refresh_selection(self, selected_card):
        for card, panel in self.cards:
            if card is None or card is selected_card:
                # Keep the slot's size while the card appears in the selection panel.
                panel.grid_remove()
            else:
                panel.grid()
