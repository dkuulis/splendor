import tkinter as tk
from tkinter import ttk

from game.constants import TOKENS

from .assets import load_image
from .styles import CARD_BACKGROUND, TOKEN_SIZE, TOKEN_SPACING, INACTIVE_PLAYER_BORDER, MARKET_CARD_HEIGHT


class SelectionPanel(tk.Frame):
    def __init__(self, parent, available_tokens, selected_tokens, on_pass, on_take, max_take=3, enabled=True,
                 on_selection=None):
        super().__init__(parent, height=MARKET_CARD_HEIGHT, background=CARD_BACKGROUND,
                         highlightthickness=1, highlightbackground=INACTIVE_PLAYER_BORDER,
                         borderwidth=0)
        self.grid_propagate(False)
        self.available_tokens = available_tokens
        self.selected_tokens = selected_tokens
        self.on_pass = on_pass
        self.on_take = on_take
        self.max_take = max_take
        self.enabled = enabled
        self.on_selection = on_selection
        self.images = {token: load_image(self, token.lower()) for token in TOKENS}
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.tokens = tk.Canvas(self, width=TOKEN_SIZE + 4 * TOKEN_SPACING, height=TOKEN_SIZE,
                                background=CARD_BACKGROUND, highlightthickness=0)
        self.tokens.grid(row=0, column=0, padx=5)
        self.go_button = ttk.Button(self, text="Go!", command=self.go, state="disabled")
        self.go_button.grid(row=0, column=1, sticky="e", padx=5)

        self.refresh()

    def refresh(self):
        self.go_button.configure(state="normal" if self.can_go else "disabled")
        self.tokens.delete("all")
        index = 0
        for token in TOKENS:
            for _ in range(self.selected_tokens.get(token, 0)):
                item = self.tokens.create_image(TOKEN_SIZE / 2 + index * TOKEN_SPACING,
                                                TOKEN_SIZE / 2, image=self.images[token])
                self.tokens.tag_bind(item, "<Button-1>",
                                     lambda event, token=token: self.deselect(token))
                index += 1
        self.tokens.configure(width=max(TOKEN_SIZE + 4 * TOKEN_SPACING,
                                        TOKEN_SIZE + (index - 1) * TOKEN_SPACING))
        self.configure(width=self.tokens.winfo_reqwidth() + self.go_button.winfo_reqwidth() + 24)

    @property
    def can_go(self):
        count = sum(self.selected_tokens.values())
        valid = all(amount == 1 and token in TOKENS and self.available_tokens.get(token, 0)
                    for token, amount in self.selected_tokens.items())
        return self.enabled and valid and count <= self.max_take

    def go(self):
        if not self.can_go:
            return
        tokens = [token for token in TOKENS if self.selected_tokens.get(token, 0)]
        if tokens:
            self.on_take(tokens)
        else:
            self.on_pass()

    def select(self, token):
        if (not self.enabled or token not in TOKENS or not self.available_tokens.get(token, 0)
                or self.selected_tokens.get(token, 0)):
            return
        self.selected_tokens[token] = 1
        self.update_selection()

    def deselect(self, token):
        if not self.enabled:
            return
        self.selected_tokens.pop(token, None)
        self.update_selection()

    def update_selection(self):
        self.refresh()
        if self.on_selection:
            self.on_selection()
