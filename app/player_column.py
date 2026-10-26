import tkinter as tk
from tkinter import ttk

from .assets import load_image
from .styles import (
    TOKEN_SIZE,
    TOKEN_SPACING,
    MARKET_CARD_HEIGHT,
    MARKET_CARD_WIDTH,
    PLAYER_CARD_OFFSET,
    TOKEN_OVERHANG,
    PLAYER_TOKENS_PER_COLUMN,
    PLAYER_PANEL_BACKGROUND,
)


class PlayerColumn(ttk.Frame):
    def __init__(self, parent, token, cards, token_count):
        super().__init__(parent, style="Player.TFrame")
        self.token = token
        self.stack = tk.Canvas(self, height=MARKET_CARD_HEIGHT,
                               highlightthickness=0, borderwidth=0,
                               background=PLAYER_PANEL_BACKGROUND)
        self.stack.pack()
        self.card_items = []
        self.token_items = []
        self.refresh(cards, token_count)

    def refresh(self, cards, token_count):
        stack_width = MARKET_CARD_WIDTH + max(0, len(cards) - 1) * PLAYER_CARD_OFFSET
        token_columns = (token_count + PLAYER_TOKENS_PER_COLUMN - 1) // PLAYER_TOKENS_PER_COLUMN
        token_width = TOKEN_SIZE + max(0, token_columns - 1) * TOKEN_SPACING if token_count else 0
        overhang = TOKEN_OVERHANG if token_count else 0
        width = max(stack_width + overhang, token_width)
        self.stack.configure(width=width)
        # Align the rightmost card and token column, leaving room for token overhang.
        start = width - overhang - stack_width
        while len(self.card_items) < len(cards):
            self.card_items.append(self.stack.create_image(0, 0, anchor="nw"))
        for index, item in enumerate(self.card_items):
            if index < len(cards):
                self.stack.coords(item, start + index * PLAYER_CARD_OFFSET, 0)
                self.stack.itemconfigure(item, image=load_image(self, cards[index].id), state="normal")
                self.stack.tag_raise(item)
            else:
                self.stack.itemconfigure(item, state="hidden")
        while len(self.token_items) < token_count:
            self.token_items.append(self.stack.create_image(0, 0, image=load_image(self, self.token.lower())))
        for index, item in enumerate(self.token_items):
            if index < token_count:
                column, row = divmod(index, PLAYER_TOKENS_PER_COLUMN)
                self.stack.coords(item, width - TOKEN_SIZE / 2 - column * TOKEN_SPACING,
                                  MARKET_CARD_HEIGHT - TOKEN_SIZE / 2 - row * TOKEN_SPACING)
                self.stack.itemconfigure(item, state="normal")
                self.stack.tag_raise(item)
            else:
                self.stack.itemconfigure(item, state="hidden")
