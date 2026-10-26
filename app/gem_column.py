import tkinter as tk
from tkinter import ttk

from .drawing import draw_gem, row_centers
from .styles import (
    GEM_RADIUS,
    GEM_SPACING,
    OUTLINE_PALETTE,
    SELECTION_MARKER_FONT,
    SELECTION_OUTLINE_COLOR,
    TEXT_PALETTE,
)

BANK_CANVAS_WIDTH = 176
BANK_CANVAS_HEIGHT = 48


class GemColumn(ttk.Frame):
    def __init__(self, parent, color, available, on_selection_changed, enabled=True):
        super().__init__(parent)
        self.color = color
        self.available = available
        self.selected = 0
        self.enabled = enabled
        self.on_selection_changed = on_selection_changed
        self.gem_items = []

        self.tokens = tk.Canvas(
            self, width=BANK_CANVAS_WIDTH, height=BANK_CANVAS_HEIGHT, highlightthickness=0,
            background=self.winfo_toplevel().cget("background"),
        )
        self.tokens.pack()

        y = BANK_CANVAS_HEIGHT / 2
        for x in row_centers(available, BANK_CANVAS_WIDTH, GEM_SPACING):
            gem = draw_gem(
                self.tokens, color, x, y, GEM_RADIUS, width=2, tags=("gem",),
            )
            marker = self.tokens.create_text(
                x, y, text="✓",
                fill=TEXT_PALETTE[color],
                font=SELECTION_MARKER_FONT,
                state="hidden", tags=("gem",),
            )
            self.gem_items.append((gem, marker))

        self.tokens.tag_bind("gem", "<Button-1>", lambda event: self.toggle_selection())
        self.tokens.tag_bind("gem", "<Enter>", lambda event: self.tokens.configure(cursor="hand2"))
        self.tokens.tag_bind("gem", "<Leave>", lambda event: self.tokens.configure(cursor=""))
        ttk.Label(self, text=color).pack()

    def toggle_selection(self):
        if not self.enabled or not self.available:
            return
        self.selected = 1 - self.selected
        self.update_selection()
        self.on_selection_changed()

    def update_selection(self):
        for index, (gem, marker) in enumerate(self.gem_items):
            selected = index < self.selected
            self.tokens.itemconfigure(
                gem,
                outline=SELECTION_OUTLINE_COLOR if selected else OUTLINE_PALETTE[self.color],
                width=4 if selected else 2,
            )
            self.tokens.itemconfigure(marker, state="normal" if selected else "hidden")
