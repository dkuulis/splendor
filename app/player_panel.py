import tkinter as tk
from tkinter import ttk

from game.constants import COLORS

from .styles import (
    MUTED_TEXT_COLOR,
    OUTLINE_PALETTE,
    PALETTE,
    POINTS_FONT,
)


class PlayerPanel(ttk.LabelFrame):
    def __init__(self, parent, player, subtitle):
        self.player = player
        discounts = player.discounts
        super().__init__(parent, text=f"{player.name}  •  {subtitle}", padding=10)
        panel = self
        ttk.Label(panel, text=str(player.points), font=POINTS_FONT).pack(side="left", padx=(0, 20))

        for color in COLORS:
            column = ttk.Frame(panel)
            column.pack(side="left", expand=True, fill="x")

            card_count, gem_count = discounts.get(color, 0), player.gems.get(color, 0)
            spacing = 28
            group_gap = 10 if card_count and gem_count else 0
            content_width = (card_count + gem_count) * spacing + group_gap
            canvas_width = max(100, content_width)

            resources = tk.Canvas(
                column, width=canvas_width, height=44, highlightthickness=0,
                background=parent.winfo_toplevel().cget("background"),
            )
            resources.pack()

            outline = OUTLINE_PALETTE[color]
            start = (canvas_width - content_width) / 2
            for card in range(card_count):
                x = start + card * spacing
                resources.create_rectangle(x + 2, 10, x + 26, 34, fill=PALETTE[color], outline=outline)
            for gem in range(gem_count):
                x = start + card_count * spacing + group_gap + gem * spacing
                resources.create_oval(x + 2, 10, x + 26, 34, fill=PALETTE[color], outline=outline)
            ttk.Label(column, text=color, foreground=MUTED_TEXT_COLOR).pack()

        ttk.Label(panel, text=f"{sum(player.gems.values())} gems", justify="right").pack(side="right")
