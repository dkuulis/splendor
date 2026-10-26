import tkinter as tk
from tkinter import ttk

from game.constants import TOKENS

from .player_column import PlayerColumn

from .styles import (
    ACTIVE_PLAYER_BORDER,
    INACTIVE_PLAYER_BORDER,
    MARKET_CARD_HEIGHT,
    PLAYER_COLUMN_GAP,
    PLAYER_PANEL_BACKGROUND,
    PLAYER_PANEL_PADDING,
)


class PlayerPanel(tk.Frame):
    def __init__(self, parent, player, active=False):
        border = ACTIVE_PLAYER_BORDER if active else INACTIVE_PLAYER_BORDER
        super().__init__(parent, background=PLAYER_PANEL_BACKGROUND, highlightthickness=2,
                         highlightbackground=border, highlightcolor=border, borderwidth=0)
        # Grid's row minimum takes effect only when there are children. Reserve
        # the same content height plus vertical padding for an empty inventory.
        self.panel = ttk.Frame(self, padding=PLAYER_PANEL_PADDING, style="Player.TFrame",
                               height=MARKET_CARD_HEIGHT + 2 * PLAYER_PANEL_PADDING)
        self.panel.pack(fill="both", expand=True)
        self.panel.rowconfigure(0, minsize=MARKET_CARD_HEIGHT)

        for index, token in enumerate(TOKENS):
            cards = [card for card in player.cards.values() if card.token == token]
            token_count = player.tokens.get(token, 0)
            if not cards and not token_count:
                continue
            column = PlayerColumn(self.panel, token, cards, token_count)
            self.panel.columnconfigure(index, weight=1)
            column.grid(row=0, column=index, sticky="ew", padx=(0, PLAYER_COLUMN_GAP))
