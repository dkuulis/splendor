import tkinter as tk
from tkinter import ttk

from .assets import load_image
from .styles import (
    MARKET_CARD_WIDTH,
    PLAYER_CARD_OFFSET,
    TOKEN_OVERHANG,
    PLAYER_PANEL_BACKGROUND,
)


class PlayerColumn(ttk.Frame):
    def __init__(self, parent, token, cards, token_count, height, disabled):
        super().__init__(parent, style="Player.TFrame")
        self.token = token
        self.height = height
        self.disabled = disabled
        self.stack = tk.Canvas(self, height=height,
                               highlightthickness=0, borderwidth=0,
                               background=PLAYER_PANEL_BACKGROUND)
        self.stack.pack()
        self.card_items = []
        self.overlay_items = []
        self.token_item = self.stack.create_image(0, 0, anchor="se")
        self.refresh(cards, token_count)

    def refresh(self, cards, token_count):
        stack_width = MARKET_CARD_WIDTH + max(0, len(cards) - 1) * PLAYER_CARD_OFFSET
        image = None
        if token_count:
            name = self.token.lower() + (str(token_count) if token_count > 1 else "")
            image = load_image(self, name)
        token_width = image.width() if image else 0
        overhang = TOKEN_OVERHANG if token_count else 0
        width = max(stack_width + overhang, token_width)
        self.stack.configure(width=width)
        # Align the pile with the bottom right, leaving room for token overhang.
        start = width - overhang - stack_width
        while len(self.card_items) < len(cards):
            self.card_items.append(self.stack.create_image(0, 0, anchor="nw"))
            if self.disabled:
                self.overlay_items.append(self.stack.create_image(
                    0, 0, anchor="nw", image=load_image(self, "disabled")))
        for index, item in enumerate(self.card_items):
            if index < len(cards):
                self.stack.coords(item, start + index * PLAYER_CARD_OFFSET, 0)
                self.stack.itemconfigure(item, image=load_image(self, cards[index].id), state="normal")
                self.stack.tag_raise(item)
            else:
                self.stack.itemconfigure(item, state="hidden")
            if self.disabled:
                overlay = self.overlay_items[index]
                self.stack.coords(overlay, start + index * PLAYER_CARD_OFFSET, 0)
                self.stack.itemconfigure(overlay, state="normal" if index < len(cards) else "hidden")
                self.stack.tag_raise(overlay)
        self.stack.coords(self.token_item, width, self.height)
        self.stack.itemconfigure(self.token_item, image=image if image else "",
                                 state="normal" if image else "hidden")
        self.stack.tag_raise(self.token_item)
