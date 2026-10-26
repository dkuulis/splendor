import tkinter as tk
from tkinter import ttk

from game.constants import GOLD, TOKENS

from .player_column import PlayerColumn

from .styles import (
    ACTIVE_PLAYER_BORDER,
    INACTIVE_PLAYER_BORDER,
    MARKET_CARD_HEIGHT,
    NOBLE_SIZE,
    PLAYER_COLUMN_GAP,
    PLAYER_PANEL_BACKGROUND,
    PLAYER_PANEL_PADDING,
)


class PlayerPanel(tk.Frame):
    def __init__(self, parent, on_select):
        border = INACTIVE_PLAYER_BORDER
        super().__init__(parent, background=PLAYER_PANEL_BACKGROUND, highlightthickness=2,
                         highlightbackground=border, highlightcolor=border, borderwidth=0)
        self.on_select = on_select
        self.enabled = False
        # Grid's row minimum takes effect only when there are children. Reserve
        # the same content height plus vertical padding for an empty inventory.
        self.panel = ttk.Frame(self, padding=PLAYER_PANEL_PADDING, style="Player.TFrame",
                               height=MARKET_CARD_HEIGHT + 2 * PLAYER_PANEL_PADDING)
        self.panel.pack(fill="both", expand=True)
        self.panel.rowconfigure(0, minsize=MARKET_CARD_HEIGHT)

        self.columns = {}
        # Nobles share the leftmost column with gold; gem columns follow canonical order.
        for index, token in enumerate(TOKENS):
            height = NOBLE_SIZE if token == GOLD else MARKET_CARD_HEIGHT
            column = PlayerColumn(self.panel, token, [], 0, height=height, disabled=False)
            column.grid(row=0, column=index, sticky="ew", padx=(0, PLAYER_COLUMN_GAP))
            self.columns[token] = column
        self.reserved = PlayerColumn(self.panel, None, [], 0,
                                     height=MARKET_CARD_HEIGHT, disabled=True)
        self.reserved.grid(row=0, column=len(TOKENS), sticky="ew")
        self.reserved.stack.bind("<Button-1>", self.select_reserved)

    def refresh(self, player, active, enabled):
        self.player = player
        self.enabled = enabled and active
        self.reserved.stack.configure(cursor="hand2" if self.enabled else "")
        border = ACTIVE_PLAYER_BORDER if active else INACTIVE_PLAYER_BORDER
        self.configure(highlightbackground=border, highlightcolor=border)
        for index, (token, column) in enumerate(self.columns.items()):
            cards = (list(player.nobles) if token == GOLD else
                     player.cards[token])
            token_count = player.tokens.get(token, 0)
            column.refresh(cards, token_count)
            visible = bool(cards or token_count)
            self.panel.columnconfigure(index, weight=1 if visible else 0)
            if visible:
                column.grid()
            else:
                column.grid_remove()
        self.reserved.refresh(player.reserved_cards, 0)
        self.panel.columnconfigure(len(TOKENS), weight=1 if player.reserved_cards else 0)
        if player.reserved_cards:
            self.reserved.grid()
        else:
            self.reserved.grid_remove()

    def refresh_selection(self, selected_card):
        for index, card in enumerate(self.player.reserved_cards):
            state = "hidden" if card is selected_card else "normal"
            self.reserved.stack.itemconfigure(self.reserved.card_items[index], state=state)
            self.reserved.stack.itemconfigure(self.reserved.overlay_items[index], state=state)

    def select_reserved(self, event):
        if not self.enabled:
            return
        # Tk's "current" tag identifies the topmost canvas item under the pointer.
        current = self.reserved.stack.find_withtag("current")
        for index, card in enumerate(self.player.reserved_cards):
            if (self.reserved.card_items[index] in current
                    or self.reserved.overlay_items[index] in current):
                self.on_select(card)
                return
