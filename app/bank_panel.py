import tkinter as tk
from tkinter import ttk

from game.constants import COLORS

from .gem_column import GemColumn


class BankPanel(ttk.Frame):
    def __init__(self, parent, bank):
        super().__init__(parent, padding=10)
        self.bank = bank
        self.columns = {}
        self.selection_text = tk.StringVar(master=self, value="Click gems to select or deselect")

        gem_row = ttk.Frame(self)
        gem_row.pack(fill="x")
        for color in COLORS:
            column = GemColumn(gem_row, color, bank.get(color, 0), self.update_selection)
            column.pack(side="left", expand=True, fill="x", padx=8)
            self.columns[color] = column

        actions = ttk.Frame(self)
        actions.pack(fill="x", pady=(12, 0))
        ttk.Label(actions, textvariable=self.selection_text).pack(side="left")
        ttk.Button(actions, text="Take selected gems", state="disabled").pack(side="right")
        ttk.Button(actions, text="Pass", state="disabled").pack(side="right", padx=8)

    def update_selection(self):
        selected = [f"{column.selected} {color}" for color, column in self.columns.items() if column.selected]
        self.selection_text.set(
            "Selected: " + ", ".join(selected) if selected
            else "Click gems to select or deselect"
        )
