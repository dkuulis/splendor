import tkinter as tk
from tkinter import ttk

from .assets import load_image
from .styles import (
    GEM_SPACING,
    GEM_SIZE,
    gem_centers,
)

BANK_CANVAS_WIDTH = GEM_SIZE + 3 * GEM_SPACING
BANK_CANVAS_HEIGHT = GEM_SIZE


class GemSelector(ttk.Frame):
    def __init__(self, parent, color, available, selected_gems, on_selection_changed, enabled=True):
        super().__init__(parent)
        self.available = available
        self.color = color
        self.selected_gems = selected_gems
        self.enabled = enabled
        self.on_selection_changed = on_selection_changed
        self.gem_items = []

        self.tokens = tk.Canvas(
            self, width=BANK_CANVAS_WIDTH, height=BANK_CANVAS_HEIGHT, highlightthickness=0,
            background=self.winfo_toplevel().cget("background"),
        )
        self.tokens.pack()
        self.image = load_image(self, color.lower())
        y = GEM_SIZE / 2
        for x in gem_centers(available, BANK_CANVAS_WIDTH, GEM_SPACING):
            gem = self.tokens.create_image(x, y, image=self.image, tags=("gem",))
            self.gem_items.append(gem)

        self.tokens.tag_bind("gem", "<Button-1>", lambda event: self.select())
        self.tokens.tag_bind("gem", "<Enter>", lambda event: self.tokens.configure(cursor="hand2"))
        self.tokens.tag_bind("gem", "<Leave>", lambda event: self.tokens.configure(cursor=""))
        self.update_selection()

    @property
    def selected(self):
        return self.selected_gems.get(self.color, 0)

    def select(self):
        if not self.enabled or not self.available or self.selected:
            return
        self.selected_gems[self.color] = 1
        self.on_selection_changed()

    def update_selection(self):
        count = max(0, self.available - self.selected)
        for gem in self.gem_items:
            self.tokens.itemconfigure(gem, state="hidden")
        for gem, x in zip(self.gem_items, gem_centers(count, BANK_CANVAS_WIDTH, GEM_SPACING)):
            self.tokens.coords(gem, x, GEM_SIZE / 2)
            self.tokens.itemconfigure(gem, state="normal")
