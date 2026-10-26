import tkinter as tk
from tkinter import ttk

from game.constants import TOKENS

from .assets import load_image
from .styles import TOKEN_PILE_HEIGHT, TOKEN_PILE_WIDTH


class SupplyPanel(ttk.Frame):
    def __init__(self, parent, on_pick):
        super().__init__(parent, padding=5)
        self.enabled = False
        self.on_pick = on_pick
        self.cells = {}
        self.counts = {}

        for row in range(3):
            self.rowconfigure(row, weight=1)
        for column in range(2):
            self.columnconfigure(column, weight=1)
        for index, token in enumerate(TOKENS):
            cell = tk.Canvas(
                self, width=TOKEN_PILE_WIDTH, height=TOKEN_PILE_HEIGHT, highlightthickness=0,
                background=self.winfo_toplevel().cget("background"),
            )
            cell.grid(row=index // 2, column=index % 2, padx=5, pady=2)
            cell.create_image(TOKEN_PILE_WIDTH / 2, TOKEN_PILE_HEIGHT / 2, tags=("gem",))
            self.cells[token] = cell
            cell.tag_bind("gem", "<Button-1>", lambda event, token=token: self.pick(token))
            cell.tag_bind("gem", "<Enter>", lambda event, cell=cell: cell.configure(cursor="hand2" if self.enabled else ""))
            cell.tag_bind("gem", "<Leave>", lambda event, cell=cell: cell.configure(cursor=""))

    def pick(self, token):
        if self.enabled:
            self.on_pick(token)

    def refresh(self, available_tokens, selected_tokens, enabled):
        self.enabled = enabled
        for token, cell in self.cells.items():
            count = max(
                0, available_tokens.get(token, 0) - selected_tokens.get(token, 0)
            )
            cell.configure(cursor="")
            if self.counts.get(token) == count:
                continue
            self.counts[token] = count
            if count:
                name = token.lower() + (str(count) if count > 1 else "")
                image = load_image(self, name)
                cell.itemconfigure("gem", image=image, state="normal")
            else:
                cell.itemconfigure("gem", image="", state="hidden")
