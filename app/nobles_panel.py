import tkinter as tk
from tkinter import ttk

from .assets import load_image
from .styles import MARKET_ROW_PADDING, NOBLE_SIZE


class NoblesPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.slots = []

    def refresh(self, nobles):
        self.nobles = nobles
        while len(self.slots) < len(nobles):
            row = len(self.slots)
            tile = tk.Canvas(self, width=NOBLE_SIZE, height=NOBLE_SIZE,
                             highlightthickness=0, borderwidth=0)
            tile.create_image(0, 0, anchor="nw")
            tile.grid(row=row, column=0, sticky="n", padx=4, pady=MARKET_ROW_PADDING)
            self.slots.append(tile)
        for index, tile in enumerate(self.slots):
            if index < len(nobles):
                tile.itemconfigure(1, image=load_image(tile, nobles[index].id))
                tile.grid()
            else:
                tile.itemconfigure(1, image="")
                tile.grid_remove()
