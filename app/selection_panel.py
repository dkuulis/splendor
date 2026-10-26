import tkinter as tk
from tkinter import ttk

from game.constants import TOKENS

from .assets import load_image
from .card_panel import CardPanel
from .styles import (CARD_BACKGROUND, TOKEN_SIZE, TOKEN_SPACING, TOKEN_GAP,
                     MARKET_CARD_HEIGHT, ACTION_BUTTON_WIDTH, ACTION_BUTTON_HEIGHT,
                     ACTION_BUTTON_TOPS, RESTART_BUTTON_HEIGHT)


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
        for button, action, top, height in zip(
                (self.action_button, self.restart_button), ("pass", "restart"),
                ACTION_BUTTON_TOPS, (ACTION_BUTTON_HEIGHT, RESTART_BUTTON_HEIGHT)):
            button.place(x=0, y=top, width=ACTION_BUTTON_WIDTH, height=height)
            self.set_button(button, action, False)
        self.configure(width=TOKEN_SIZE + 4 * TOKEN_SPACING + ACTION_BUTTON_WIDTH + 24)

    def refresh(self, state, selection, enabled):
        self.state = state
        self.selection = selection
        self.enabled = enabled
        affordable = self.enabled and state.can_buy(selection.card)
        self.card.refresh(selection.card, affordable=affordable, enabled=self.enabled)
        self.card.itemconfigure(self.disabled_overlay,
                                state="normal" if selection.card is not None and not affordable
                                else "hidden")
        if selection.card is not None:
            self.card.grid()
            if selection.tokens:
                self.tokens.grid(padx=(0, 10))
            else:
                self.tokens.grid_remove()
        else:
            self.card.grid_remove()
            self.tokens.grid(padx=0)
        piles = []
        for token, item in self.items.items():
            count = selection.tokens.get(token, 0)
            self.tokens.itemconfigure(item, state="normal" if count else "hidden")
            if count:
                name = token.lower() + (str(count) if count > 1 else "")
                image = load_image(self, name)
                self.tokens.itemconfigure(item, image=image)
                piles.append((item, image.width(), image.height()))
        height = max([TOKEN_SIZE] + [height for _, _, height in piles])
        left = 0
        for item, width, _ in piles:
            self.tokens.coords(item, left + width / 2, height / 2)
            left += width + TOKEN_GAP
        self.tokens.configure(width=max(TOKEN_SIZE, left - TOKEN_GAP),
                              height=height)
        if state.turn.finished:
            result = {0: "win", 1: "loose", None: "tie"}[state.turn.winner]
            self.set_button(self.action_button, result, False)
        else:
            self.set_button(self.action_button, selection.action_kind, self.can_go)
        self.set_button(self.restart_button, "restart", True)

    def set_button(self, button, action, enabled):
        suffix = "" if action == "restart" else "2"
        disabled_image = load_image(self, f"button_{action}_disabled{suffix}")
        image = (load_image(self, f"button_{action}_enabled{suffix}"),
                 "disabled", disabled_image) if enabled else (disabled_image,)
        button.configure(
            text=action.capitalize(),
            image=image,
            state="normal" if enabled else "disabled")

    def deselect(self, token):
        if self.enabled and self.selection.can_deselect_token(token, self.state):
            self.on_deselect(token)

    @property
    def can_go(self):
        return self.enabled and self.selection.can_perform_action(self.state)

    def go(self):
        if self.can_go:
            self.on_action()
