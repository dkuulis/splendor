import tkinter as tk
from tkinter import ttk

from game.constants import GOLD, TOKENS

from .player_column import PlayerColumn

from .styles import (
    MARKET_CARD_HEIGHT,
    NOBLE_SIZE,
    PLAYER_COLUMN_GAP,
    PLAYER_PANEL_BACKGROUND,
    PLAYER_PANEL_PADDING,
)


class PlayerPanel(tk.Frame):
    def __init__(self, parent, on_select, can_select, on_token, can_select_token):
        super().__init__(parent, background=PLAYER_PANEL_BACKGROUND,
                         highlightthickness=0, borderwidth=0)
        self.on_select = on_select
        self.can_select = can_select
        self.on_token = on_token
        self.can_select_token = can_select_token
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
            column.stack.tag_bind(column.token_item, "<Button-1>",
                                  lambda event, token=token: self.select_token(token))
            column.stack.tag_bind(column.token_item, "<Enter>",
                                  lambda event, token=token, stack=column.stack:
                                  stack.configure(cursor="hand2" if self.enabled
                                                  and self.can_select_token(token) else ""))
            column.stack.tag_bind(column.token_item, "<Leave>",
                                  lambda event, stack=column.stack: stack.configure(cursor=""))
        self.reserved = PlayerColumn(self.panel, None, [], 0,
                                     height=MARKET_CARD_HEIGHT, disabled=True)
        self.reserved.grid(row=0, column=len(TOKENS), sticky="ew")
        self.reserved.stack.bind("<Button-1>", self.select_reserved)

    def refresh(self, player, active, enabled, selected_card, selected_tokens):
        self.player = player
        self.enabled = enabled and active
        self.reserved.stack.configure(
            cursor="hand2" if self.enabled and any(self.can_select(card)
                                                  for card in player.reserved_cards) else "")
        for index, (token, column) in enumerate(self.columns.items()):
            cards = (list(player.nobles) if token == GOLD else
                     player.cards[token])
            token_count = player.tokens.get(token, 0)
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
        self.refresh_selection(selected_card, selected_tokens)

    def refresh_selection(self, selected_card, selected_tokens):
        for token, column in self.columns.items():
            cards = list(self.player.nobles) if token == GOLD else self.player.cards[token]
            column.refresh(cards, self.player.tokens.get(token, 0) - selected_tokens.get(token, 0))
            column.stack.configure(cursor="")
        for index, card in enumerate(self.player.reserved_cards):
            state = "hidden" if card is selected_card else "normal"
            self.reserved.stack.itemconfigure(self.reserved.card_items[index], state=state)
            self.reserved.stack.itemconfigure(self.reserved.overlay_items[index], state=state)

    def select_token(self, token):
        if self.enabled and self.can_select_token(token):
            self.on_token(token)

    def select_reserved(self, event):
        if not self.enabled:
            return
        # Tk's "current" tag identifies the topmost canvas item under the pointer.
        current = self.reserved.stack.find_withtag("current")
        for index, card in enumerate(self.player.reserved_cards):
            if (self.reserved.card_items[index] in current
                    or self.reserved.overlay_items[index] in current):
                if self.can_select(card):
                    self.on_select(card)
                return
