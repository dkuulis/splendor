import tkinter as tk
from tkinter import ttk

from game.constants import COLORS

from .gem_column import GemColumn


class BankPanel(ttk.Frame):
    def __init__(self, parent, bank, on_pass=None, on_take=None, max_take=3):
        super().__init__(parent, padding=10)
        self.bank = bank
        self.on_take = on_take
        self.max_take = max_take
        self.finished = False
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
        self.take_button = ttk.Button(actions, text="Take selected gems", command=self.take_selected, state="disabled")
        self.take_button.pack(side="right")
        self.pass_button = ttk.Button(actions, text="Pass", command=on_pass, state="normal" if on_pass else "disabled")
        self.pass_button.pack(side="right", padx=8)

    def reset_selection(self, finished=False):
        self.finished = finished
        for column in self.columns.values():
            column.selected = 0
            column.enabled = not finished
            column.update_selection()
        self.update_selection()
        if finished:
            self.pass_button.configure(state="disabled")
            self.selection_text.set("Game over")

    def take_selected(self):
        colors = [color for color, column in self.columns.items() if column.selected]
        if not self.finished and self.on_take and 1 <= len(colors) <= self.max_take:
            self.on_take(colors)

    def update_selection(self):
        selected = [f"{column.selected} {color}" for color, column in self.columns.items() if column.selected]
        self.selection_text.set(
            "Selected: " + ", ".join(selected) if selected
            else "Click gems to select or deselect"
        )
        self.take_button.configure(state="normal" if self.on_take and not self.finished and 1 <= len(selected) <= self.max_take else "disabled")
        if not self.finished and len(selected) > self.max_take:
            self.selection_text.set(f"Select at most {self.max_take} gems; your inventory limit is included.")
