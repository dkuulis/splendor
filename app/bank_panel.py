from tkinter import ttk

from game.constants import COLORS

from .gem_selector import GemSelector


class BankPanel(ttk.Frame):
    def __init__(self, parent, bank, on_pass=None, on_take=None, max_take=3, enabled=True):
        super().__init__(parent, padding=10)
        self.on_take = on_take
        self.max_take = max_take
        self.enabled = enabled
        self.columns = {}

        self.pass_button = ttk.Button(self, text="Pass", command=on_pass, state="normal" if on_pass and enabled else "disabled")
        self.pass_button.pack(fill="x", pady=(0, 6))

        gem_rows = ttk.Frame(self)
        gem_rows.pack(fill="both", expand=True)
        for color in COLORS:
            column = GemSelector(gem_rows, color, bank.get(color, 0), self.update_selection, enabled=enabled)
            column.pack(expand=True, fill="x", pady=8)
            self.columns[color] = column

        self.take_button = ttk.Button(self, text="Take selected gems", command=self.take_selected, state="disabled")
        self.take_button.pack(fill="x", pady=(12, 0))
        self.update_selection()

    @property
    def selected_colors(self):
        return [color for color, column in self.columns.items() if column.selected]

    def take_selected(self):
        colors = self.selected_colors
        if self.enabled and self.on_take and 1 <= len(colors) <= self.max_take:
            self.on_take(colors)

    def update_selection(self):
        colors = self.selected_colors
        self.take_button.configure(state="normal" if self.on_take and self.enabled and 1 <= len(colors) <= self.max_take else "disabled")
