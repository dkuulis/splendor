from tkinter import ttk

from game.constants import COLORS

from .gem_selector import GemSelector


class BankPanel(ttk.Frame):
    def __init__(self, parent, bank, selected_gems, on_pass=None, on_take=None, max_take=3, enabled=True,
                 on_selection=None):
        super().__init__(parent, padding=5)
        self.on_pass = on_pass
        self.selected_gems = selected_gems
        self.on_take = on_take
        self.max_take = max_take
        self.enabled = enabled
        self.on_selection = on_selection
        self.columns = {}

        gem_rows = ttk.Frame(self)
        gem_rows.pack(fill="both", expand=True)
        for color in COLORS:
            available = bank.get(color, 0)
            if not available:
                continue
            column = GemSelector(gem_rows, color, available, selected_gems,
                                 self.update_selection, enabled=enabled)
            column.pack(expand=True, fill="x", pady=2)
            self.columns[color] = column

        self.update_selection()

    @property
    def selected_colors(self):
        return [color for color in COLORS if self.selected_gems.get(color, 0)]

    @property
    def can_go(self):
        count = sum(self.selected_gems.values())
        valid = all(amount == 1 and color in self.columns
                    for color, amount in self.selected_gems.items())
        return self.enabled and valid and bool(
            self.on_pass if count == 0 else self.on_take and count <= self.max_take
        )

    def go(self):
        if not self.can_go:
            return
        colors = self.selected_colors
        if colors:
            self.on_take(colors)
        else:
            self.on_pass()

    def update_selection(self):
        for column in self.columns.values():
            column.update_selection()
        if self.on_selection:
            self.on_selection(self.can_go)

    def deselect(self, color):
        if not self.enabled:
            return
        self.selected_gems.pop(color, None)
        self.update_selection()
