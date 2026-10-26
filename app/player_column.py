import tkinter as tk
from tkinter import ttk

from .styles import MUTED_TEXT_COLOR, OUTLINE_PALETTE, PALETTE, PLAYER_PANEL_BACKGROUND


class PlayerColumn(ttk.Frame):
    def __init__(self, parent, color, card_count, gem_count):
        super().__init__(parent, style="Player.TFrame")
        spacing = 28
        content_width = max(card_count, gem_count) * spacing
        canvas_width = max(100, content_width)

        resources = tk.Canvas(
            self, width=canvas_width, height=72, highlightthickness=0,
            background=PLAYER_PANEL_BACKGROUND,
        )
        resources.pack()

        outline = OUTLINE_PALETTE[color]
        start = (canvas_width - card_count * spacing) / 2
        for card in range(card_count):
            x = start + card * spacing
            resources.create_rectangle(x + 2, 6, x + 26, 30, fill=PALETTE[color], outline=outline)
        start = (canvas_width - gem_count * spacing) / 2
        for gem in range(gem_count):
            x = start + gem * spacing
            resources.create_oval(x + 2, 40, x + 26, 64, fill=PALETTE[color], outline=outline)
        ttk.Label(self, text=color, foreground=MUTED_TEXT_COLOR, style="Player.TLabel").pack()
