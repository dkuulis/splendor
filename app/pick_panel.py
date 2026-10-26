import tkinter as tk
from tkinter import ttk

from game.constants import COLORS

from .assets import load_image
from .styles import CARD_BACKGROUND, GEM_SIZE, GEM_SPACING, INACTIVE_PLAYER_BORDER, MARKET_CARD_HEIGHT


class PickPanel(tk.Frame):
    def __init__(self, parent, selected_gems, on_go, on_deselect):
        super().__init__(parent, height=MARKET_CARD_HEIGHT, background=CARD_BACKGROUND,
                         highlightthickness=1, highlightbackground=INACTIVE_PLAYER_BORDER,
                         borderwidth=0)
        self.grid_propagate(False)
        self.selected_gems = selected_gems
        self.on_deselect = on_deselect
        self.images = {color: load_image(self, color.lower()) for color in COLORS}
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.tokens = tk.Canvas(self, width=GEM_SIZE + 4 * GEM_SPACING, height=GEM_SIZE,
                                background=CARD_BACKGROUND, highlightthickness=0)
        self.tokens.grid(row=0, column=0, padx=5)
        self.go_button = ttk.Button(self, text="Go!", command=on_go, state="disabled")
        self.go_button.grid(row=0, column=1, sticky="e", padx=5)

    def refresh(self, enabled):
        self.go_button.configure(state="normal" if enabled else "disabled")
        self.tokens.delete("all")
        index = 0
        for color in COLORS:
            for _ in range(self.selected_gems.get(color, 0)):
                item = self.tokens.create_image(GEM_SIZE / 2 + index * GEM_SPACING,
                                                GEM_SIZE / 2, image=self.images[color])
                self.tokens.tag_bind(item, "<Button-1>",
                                     lambda event, color=color: self.on_deselect(color))
                index += 1
        self.tokens.configure(width=max(GEM_SIZE + 4 * GEM_SPACING,
                                        GEM_SIZE + (index - 1) * GEM_SPACING))
        self.configure(width=self.tokens.winfo_reqwidth() + self.go_button.winfo_reqwidth() + 24)
