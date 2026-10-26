import tkinter as tk
from tkinter import ttk

from game.constants import TOKENS

from .assets import load_image
from .card_panel import CardPanel
from .styles import (CARD_BACKGROUND, TOKEN_SIZE, TOKEN_SPACING, INACTIVE_PLAYER_BORDER,
                     MARKET_CARD_HEIGHT)


class SelectionPanel(tk.Frame):
    def __init__(self, parent, state, on_action, on_card, on_deselect,
                 enabled=True):
        super().__init__(parent, height=MARKET_CARD_HEIGHT + 2, background=CARD_BACKGROUND,
                         highlightthickness=1, highlightbackground=INACTIVE_PLAYER_BORDER,
                         borderwidth=0)
        self.grid_propagate(False)
        self.state = state
        self.enabled = enabled
        self.on_action = on_action
        self.on_card = on_card
        self.on_deselect = on_deselect
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.card = CardPanel(self, on_buy=on_card)
        self.card.grid(row=0, column=0)
        self.tokens = tk.Canvas(self, width=TOKEN_SIZE + 4 * TOKEN_SPACING, height=TOKEN_SIZE,
                                background=CARD_BACKGROUND, highlightthickness=0)
        self.tokens.grid(row=0, column=0, padx=5)
        self.items = {}
        for token in TOKENS:
            item = self.tokens.create_image(0, TOKEN_SIZE / 2, image=load_image(self, token.lower()),
                                            state="hidden")
            self.items[token] = item
            self.tokens.tag_bind(item, "<Button-1>",
                                 lambda event, token=token: self.deselect(token))
        self.go_button = ttk.Button(self, command=self.go)
        self.go_button.grid(row=0, column=1, sticky="e", padx=5)
        self.refresh()
        self.configure(width=TOKEN_SIZE + 4 * TOKEN_SPACING + self.go_button.winfo_reqwidth() + 24)

    def refresh(self):
        state = self.state
        self.card.refresh(state.selected_card, affordable=self.enabled)
        if state.selected_card is not None:
            self.tokens.grid_remove()
            self.card.grid()
        else:
            self.card.grid_remove()
            self.tokens.grid()
        index = 0
        for token, item in self.items.items():
            selected = bool(state.selected_tokens.get(token, 0))
            self.tokens.itemconfigure(item, state="normal" if selected else "hidden")
            if selected:
                self.tokens.coords(item, TOKEN_SIZE / 2 + index * TOKEN_SPACING, TOKEN_SIZE / 2)
                index += 1
        self.go_button.configure(text=state.action_label, state="normal" if self.can_go else "disabled")

    def deselect(self, token):
        if self.enabled:
            self.on_deselect(token)

    @property
    def can_go(self):
        return self.enabled and self.state.action_error is None

    def go(self):
        if self.can_go:
            self.on_action()
