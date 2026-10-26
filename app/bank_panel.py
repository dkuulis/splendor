from tkinter import ttk

from game.constants import COLORS

from .gem_selector import GemSelector


class BankPanel(ttk.Frame):
    def __init__(self, parent, bank, on_pass=None, on_take=None, max_take=3, enabled=True):
        super().__init__(parent, padding=10)
        self.on_pass = on_pass
        self.on_take = on_take
        self.max_take = max_take
        self.enabled = enabled
        self.columns = {}

        gem_rows = ttk.Frame(self)
        gem_rows.pack(fill="both", expand=True)
        for color in COLORS:
            available = bank.get(color, 0)
            if not available:
                continue
            column = GemSelector(gem_rows, color, available, self.update_selection, enabled=enabled)
            column.pack(expand=True, fill="x", pady=8)
            self.columns[color] = column

        self.go_button = ttk.Button(self, text="Go!", command=self.go, state="disabled")
        self.go_button.pack(fill="x", pady=(12, 0))
        self.update_selection()

    @property
    def selected_colors(self):
        return [color for color, column in self.columns.items() if column.selected]

    @property
    def can_go(self):
        count = len(self.selected_colors)
        return self.enabled and bool(self.on_pass if count == 0 else self.on_take and count <= self.max_take)

    def go(self):
        if not self.can_go:
            return
        colors = self.selected_colors
        if colors:
            self.on_take(colors)
        else:
            self.on_pass()

    def update_selection(self):
        self.go_button.configure(state="normal" if self.can_go else "disabled")
