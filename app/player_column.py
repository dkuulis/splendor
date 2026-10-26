import tkinter as tk
from tkinter import ttk

from .card_panel import CardPanel
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
        stack_width = MARKET_CARD_WIDTH + max(0, len(cards) - 1) * PLAYER_CARD_OFFSET
        token_columns = (token_count + PLAYER_TOKENS_PER_COLUMN - 1) // PLAYER_TOKENS_PER_COLUMN
        token_width = TOKEN_SIZE + max(0, token_columns - 1) * TOKEN_SPACING if token_count else 0
        overhang = TOKEN_OVERHANG if token_count else 0
        width = max(stack_width + overhang, token_width)

        stack = tk.Canvas(self, width=width, height=MARKET_CARD_HEIGHT,
                          highlightthickness=0, borderwidth=0,
                          background=PLAYER_PANEL_BACKGROUND)
        stack.pack()
        self.images = []
        # Keep the right card edge aligned with the rightmost token column, while
        # allowing extra token columns to extend left without clipping.
        start = width - overhang - stack_width
        for index, card in enumerate(cards):
            self.images.extend(CardPanel.draw(stack, card, x=start + index * PLAYER_CARD_OFFSET, owned=True))

        if token_count:
            self.token_image = load_image(self, token.lower())
            for index in range(token_count):
                column, row = divmod(index, PLAYER_TOKENS_PER_COLUMN)
                x = width - TOKEN_SIZE / 2 - column * TOKEN_SPACING
                y = MARKET_CARD_HEIGHT - TOKEN_SIZE / 2 - row * TOKEN_SPACING
                stack.create_image(x, y, image=self.token_image)
