import tkinter as tk
from tkinter import ttk

from game.constants import TOKENS

from .assets import load_image
from .card_panel import CardPanel
from .styles import (CARD_BACKGROUND, TOKEN_SIZE, TOKEN_SPACING,
                     MARKET_CARD_HEIGHT, ACTION_BUTTON_WIDTH, ACTION_BUTTON_HEIGHT,
                     ACTION_BUTTON_TOPS)


class SelectionPanel(tk.Frame):
    def __init__(self, parent, on_action, on_card, on_deselect, on_restart):
        super().__init__(parent, height=MARKET_CARD_HEIGHT + 2, background=CARD_BACKGROUND,
                         highlightthickness=0,
                         borderwidth=0)
        self.grid_propagate(False)
        self.enabled = False
        self.on_action = on_action
        self.on_deselect = on_deselect
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.contents = tk.Frame(self, background=CARD_BACKGROUND, borderwidth=0)
        self.contents.grid(row=0, column=0)
        self.card = CardPanel(self.contents, on_select=on_card)
        self.disabled_overlay = self.card.create_image(
            0, 0, anchor="nw", image=load_image(self, "disabled"), state="hidden")
        self.card.grid(row=0, column=1)
        self.tokens = tk.Canvas(self.contents, width=TOKEN_SIZE, height=TOKEN_SIZE,
                                background=CARD_BACKGROUND, highlightthickness=0)
        self.tokens.grid(row=0, column=0)
        self.items = {}
        for token in TOKENS:
            item = self.tokens.create_image(0, TOKEN_SIZE / 2, image=load_image(self, token.lower()),
                                            state="hidden")
            self.items[token] = item
            self.tokens.tag_bind(item, "<Button-1>",
                                 lambda event, token=token: self.deselect(token))
        self.actions = tk.Frame(self, width=ACTION_BUTTON_WIDTH, height=MARKET_CARD_HEIGHT,
                                background=CARD_BACKGROUND, borderwidth=0)
        self.actions.grid(row=0, column=2, padx=5)
        self.action_button = ttk.Button(self.actions, style="Action.TButton",
                                        command=self.go, state="disabled", compound="none")
        self.restart_button = ttk.Button(self.actions, style="Action.TButton",
                                         command=on_restart, state="disabled", compound="none")
        for button, action, top in zip((self.action_button, self.restart_button),
                                       ("pass", "restart"), ACTION_BUTTON_TOPS):
            button.place(x=0, y=top, width=ACTION_BUTTON_WIDTH, height=ACTION_BUTTON_HEIGHT)
            self.set_button(button, action, False)
        self.configure(width=TOKEN_SIZE + 4 * TOKEN_SPACING + ACTION_BUTTON_WIDTH + 24)

    def refresh(self, state, enabled):
        self.state = state
        self.enabled = enabled
        affordable = self.enabled and state.selected_card_affordable
        self.card.refresh(state.selection.card, affordable=affordable, enabled=self.enabled)
        self.card.itemconfigure(self.disabled_overlay,
                                state="normal" if state.selection.card is not None and not affordable
                                else "hidden")
        if state.selection.card is not None:
            self.card.grid()
            if state.selection.tokens:
                self.tokens.grid(padx=(0, 10))
            else:
                self.tokens.grid_remove()
        else:
            self.card.grid_remove()
            self.tokens.grid(padx=0)
        index = 0
        for token, item in self.items.items():
            selected = bool(state.selection.tokens.get(token, 0))
            self.tokens.itemconfigure(item, state="normal" if selected else "hidden")
            if selected:
                self.tokens.coords(item, TOKEN_SIZE / 2 + index * TOKEN_SPACING, TOKEN_SIZE / 2)
                index += 1
        self.tokens.configure(width=TOKEN_SIZE + max(0, index - 1) * TOKEN_SPACING)
        self.set_button(self.action_button, state.selection.action_kind, self.can_go)
        self.set_button(self.restart_button, "restart", True)

    def set_button(self, button, action, enabled):
        button.configure(
            text=action.capitalize(),
            image=(load_image(self, f"button_{action}_enabled"),
                   "disabled", load_image(self, f"button_{action}_disabled")),
            state="normal" if enabled else "disabled")

    def deselect(self, token):
        if self.enabled:
            self.on_deselect(token)

    @property
    def can_go(self):
        return self.enabled and self.state.action_error is None

    def go(self):
        if self.can_go:
            self.on_action()
