import tkinter as tk
from tkinter import ttk

from game.constants import COLORS

from .styles import (
    OUTLINE_PALETTE,
    PALETTE,
    SELECTION_MARKER_FONT,
    SELECTION_OUTLINE_COLOR,
    TEXT_PALETTE,
)


class BankPanel(ttk.Frame):
    def __init__(self, parent, bank):
        super().__init__(parent, padding=10)
        self.bank = bank

        self.selected = {}
        self.gem_stacks = {}
        self.selection_text = tk.StringVar(master=self, value="Click gems to select or deselect")

        for color in COLORS:
            available = self.bank.get(color, 0)
            column = ttk.Frame(self)
            column.pack(side="left", expand=True, fill="x", padx=8)
            variable = tk.IntVar(master=self, value=0)
            self.selected[color] = variable

            tokens = tk.Canvas(
                column, width=176, height=48, highlightthickness=0,
                background=parent.winfo_toplevel().cget("background"),
            )
            tokens.pack()

            start = (176 - available * 42) / 2
            gem_items = []
            for token in range(available):
                x = start + token * 42
                gem = tokens.create_oval(
                    x + 2, 5, x + 40, 43,
                    fill=PALETTE[color],
                    outline=OUTLINE_PALETTE[color],
                    width=2,
                    tags=("gem",),
                )
                marker = tokens.create_text(
                    x + 21, 24, text="✓",
                    fill=TEXT_PALETTE[color],
                    font=SELECTION_MARKER_FONT,
                    state="hidden", tags=("gem",),
                )
                gem_items.append((gem, marker))

            self.gem_stacks[color] = (tokens, gem_items)
            tokens.tag_bind("gem", "<Button-1>", lambda event, selected=variable: self.toggle_gem(selected))
            tokens.tag_bind("gem", "<Enter>", lambda event, canvas=tokens: canvas.configure(cursor="hand2"))
            tokens.tag_bind("gem", "<Leave>", lambda event, canvas=tokens: canvas.configure(cursor=""))
            ttk.Label(column, text=color).pack()

    def toggle_gem(self, selected):
        selected.set(1 - selected.get())
        self.update_selection()

    def update_selection(self):
        for color, variable in self.selected.items():
            canvas, gem_items = self.gem_stacks[color]
            for index, (gem, marker) in enumerate(gem_items):
                selected = index < variable.get()
                canvas.itemconfigure(
                    gem,
                    outline=SELECTION_OUTLINE_COLOR if selected else OUTLINE_PALETTE[color],
                    width=4 if selected else 2,
                )
                canvas.itemconfigure(marker, state="normal" if selected else "hidden")

        selected = [f"{variable.get()} {color}" for color, variable in self.selected.items() if variable.get()]
        self.selection_text.set(
            "Selected: " + ", ".join(selected) if selected
            else "Click gems to select or deselect"
        )
