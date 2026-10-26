import tkinter as tk
from tkinter import ttk

from game.constants import COLORS

from .assets import load_image
from .styles import BANK_PILE_HEIGHT, BANK_PILE_WIDTH


class BankPanel(ttk.Frame):
    def __init__(self, parent, bank, selected_gems, on_pick, enabled=True):
        super().__init__(parent, padding=5)
        self.bank = bank
        self.selected_gems = selected_gems
        self.cells = {}
        self.images = []

        for row in range(3):
            self.rowconfigure(row, weight=1)
        for column in range(2):
            self.columnconfigure(column, weight=1)
        for index, color in enumerate((*COLORS, "Gold")):
            cell = tk.Canvas(
                self, width=BANK_PILE_WIDTH, height=BANK_PILE_HEIGHT, highlightthickness=0,
                background=self.winfo_toplevel().cget("background"),
            )
            cell.grid(row=index // 2, column=index % 2, padx=5, pady=2)
            cell.create_image(BANK_PILE_WIDTH / 2, BANK_PILE_HEIGHT / 2, tags=("gem",))
            self.cells[color] = cell
            if enabled and color != "Gold":
                cell.tag_bind("gem", "<Button-1>", lambda event, color=color: on_pick(color))
                cell.tag_bind("gem", "<Enter>", lambda event, cell=cell: cell.configure(cursor="hand2"))
                cell.tag_bind("gem", "<Leave>", lambda event, cell=cell: cell.configure(cursor=""))
        self.refresh()

    def refresh(self):
        self.images.clear()
        for color, cell in self.cells.items():
            # Gold is a display-only placeholder until joker rules are implemented.
            count = 5 if color == "Gold" else max(
                0, self.bank.get(color, 0) - self.selected_gems.get(color, 0)
            )
            cell.configure(cursor="")
            if count:
                name = color.lower() + (str(count) if count > 1 else "")
                image = load_image(self, name)
                self.images.append(image)  # Keep displayed images alive for Tkinter.
                cell.itemconfigure("gem", image=image, state="normal")
            else:
                cell.itemconfigure("gem", image="", state="hidden")
