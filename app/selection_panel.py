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
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.images = []
        if state.selected_card is not None:
            self.card = CardPanel(self, state.selected_card, on_card, affordable=enabled)
            self.card.grid(row=0, column=0)
        else:
            self.tokens = tk.Canvas(self, width=TOKEN_SIZE + 4 * TOKEN_SPACING, height=TOKEN_SIZE,
                                    background=CARD_BACKGROUND, highlightthickness=0)
            self.tokens.grid(row=0, column=0, padx=5)
            index = 0
            for token in TOKENS:
                for _ in range(state.selected_tokens.get(token, 0)):
                    image = load_image(self, token.lower())
                    self.images.append(image)
                    item = self.tokens.create_image(TOKEN_SIZE / 2 + index * TOKEN_SPACING,
                                                    TOKEN_SIZE / 2, image=image)
                    if enabled:
                        self.tokens.tag_bind(item, "<Button-1>",
                                             lambda event, token=token: on_deselect(token))
                    index += 1
        self.go_button = ttk.Button(self, text=state.action_label, command=self.go,
                                    state="normal" if self.can_go else "disabled")
        self.go_button.grid(row=0, column=1, sticky="e", padx=5)
        self.configure(width=TOKEN_SIZE + 4 * TOKEN_SPACING + self.go_button.winfo_reqwidth() + 24)

    @property
    def can_go(self):
        return self.enabled and self.state.action_error is None

    def go(self):
        if self.can_go:
            self.on_action()
