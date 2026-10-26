import tkinter as tk
from tkinter import ttk

from game.constants import COLORS

from .gem_column import GemColumn


class BankPanel(ttk.Frame):
    def __init__(self, parent, bank, on_pass=None, on_take=None, max_take=3, enabled=True, disabled_text="Game over"):
        super().__init__(parent, padding=10)
        self.bank = bank
        self.on_take = on_take
        self.max_take = max_take
        self.enabled = enabled
        self.disabled_text = disabled_text
        self.columns = {}
        self.selection_text = tk.StringVar(master=self, value="Click gems to select or deselect")

        gem_row = ttk.Frame(self)
        gem_row.pack(fill="x")
        for color in COLORS:
            column = GemColumn(gem_row, color, bank.get(color, 0), self.update_selection, enabled=enabled)
            column.pack(side="left", expand=True, fill="x", padx=8)
            self.columns[color] = column

        actions = ttk.Frame(self)
        actions.pack(fill="x", pady=(12, 0))
        ttk.Label(actions, textvariable=self.selection_text).pack(side="left")
        self.take_button = ttk.Button(actions, text="Take selected gems", command=self.take_selected, state="disabled")
        self.take_button.pack(side="right")
        self.pass_button = ttk.Button(actions, text="Pass", command=on_pass, state="normal" if on_pass and enabled else "disabled")
        self.pass_button.pack(side="right", padx=8)
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
        selected = [f"1 {color}" for color in colors]
        self.selection_text.set(
            "Selected: " + ", ".join(selected) if selected
            else "Click gems to select or deselect"
        )
        self.take_button.configure(state="normal" if self.on_take and self.enabled and 1 <= len(selected) <= self.max_take else "disabled")
        if not self.enabled:
            self.selection_text.set(self.disabled_text)
        elif len(colors) > self.max_take:
            self.selection_text.set(f"Select at most {self.max_take} gems; your inventory limit is included.")
