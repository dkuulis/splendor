import tkinter as tk
from tkinter import ttk

from game.constants import COLORS

from .assets import load_image
from .styles import CARD_BACKGROUND, GEM_SIZE, GEM_SPACING, INACTIVE_PLAYER_BORDER, MARKET_CARD_HEIGHT


class PickPanel(tk.Frame):
    def __init__(self, parent, bank, selected_gems, on_pass, on_take, max_take=3, enabled=True,
                 on_selection=None):
        super().__init__(parent, height=MARKET_CARD_HEIGHT, background=CARD_BACKGROUND,
                         highlightthickness=1, highlightbackground=INACTIVE_PLAYER_BORDER,
                         borderwidth=0)
        self.grid_propagate(False)
        self.bank = bank
        self.selected_gems = selected_gems
        self.on_pass = on_pass
        self.on_take = on_take
        self.max_take = max_take
        self.enabled = enabled
        self.on_selection = on_selection
        self.images = {color: load_image(self, color.lower()) for color in COLORS}
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.tokens = tk.Canvas(self, width=GEM_SIZE + 4 * GEM_SPACING, height=GEM_SIZE,
                                background=CARD_BACKGROUND, highlightthickness=0)
        self.tokens.grid(row=0, column=0, padx=5)
        self.go_button = ttk.Button(self, text="Go!", command=self.go, state="disabled")
        self.go_button.grid(row=0, column=1, sticky="e", padx=5)

        self.refresh()

    def refresh(self):
        self.go_button.configure(state="normal" if self.can_go else "disabled")
        self.tokens.delete("all")
        index = 0
        for color in COLORS:
            for _ in range(self.selected_gems.get(color, 0)):
                item = self.tokens.create_image(GEM_SIZE / 2 + index * GEM_SPACING,
                                                GEM_SIZE / 2, image=self.images[color])
                self.tokens.tag_bind(item, "<Button-1>",
                                     lambda event, color=color: self.deselect(color))
                index += 1
        self.tokens.configure(width=max(GEM_SIZE + 4 * GEM_SPACING,
                                        GEM_SIZE + (index - 1) * GEM_SPACING))
        self.configure(width=self.tokens.winfo_reqwidth() + self.go_button.winfo_reqwidth() + 24)

    @property
    def can_go(self):
        count = sum(self.selected_gems.values())
        valid = all(amount == 1 and color in COLORS and self.bank.get(color, 0)
                    for color, amount in self.selected_gems.items())
        return self.enabled and valid and count <= self.max_take

    def go(self):
        if not self.can_go:
            return
        colors = [color for color in COLORS if self.selected_gems.get(color, 0)]
        if colors:
            self.on_take(colors)
        else:
            self.on_pass()

    def select(self, color):
        if (not self.enabled or color not in COLORS or not self.bank.get(color, 0)
                or self.selected_gems.get(color, 0)):
            return
        self.selected_gems[color] = 1
        self.update_selection()

    def deselect(self, color):
        if not self.enabled:
            return
        self.selected_gems.pop(color, None)
        self.update_selection()

    def update_selection(self):
        self.refresh()
        if self.on_selection:
            self.on_selection()
