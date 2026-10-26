import tkinter as tk
from tkinter import ttk

from game.constants import COLORS

from .styles import (
    ACTIVE_PLAYER_BORDER,
    MUTED_TEXT_COLOR,
    OUTLINE_PALETTE,
    PALETTE,
    PLAYER_PANEL_BACKGROUND,
    POINTS_FONT,
)


class PlayerPanel(tk.Frame):
    def __init__(self, parent, player, subtitle, active=False):
        self.player = player
        discounts = player.discounts
        style = ttk.Style(parent)
        for name in ("Player.TLabelframe", "Player.TLabelframe.Label", "Player.TFrame", "Player.TLabel"):
            style.configure(name, background=PLAYER_PANEL_BACKGROUND)
        border = ACTIVE_PLAYER_BORDER if active else PLAYER_PANEL_BACKGROUND
        super().__init__(parent, background=PLAYER_PANEL_BACKGROUND, highlightthickness=2,
                         highlightbackground=border, highlightcolor=border, borderwidth=0)
        self.panel = ttk.LabelFrame(self, text=f"{player.name}  •  {subtitle}", padding=10, style="Player.TLabelframe")
        self.panel.pack(fill="both", expand=True)
        ttk.Label(self.panel, text=str(player.points), font=POINTS_FONT, style="Player.TLabel").pack(side="left", padx=(0, 20))

        for color in COLORS:
            column = ttk.Frame(self.panel, style="Player.TFrame")
            column.pack(side="left", expand=True, fill="x")

            card_count, gem_count = discounts.get(color, 0), player.gems.get(color, 0)
            spacing = 28
            group_gap = 10 if card_count and gem_count else 0
            content_width = (card_count + gem_count) * spacing + group_gap
            canvas_width = max(100, content_width)

            resources = tk.Canvas(
                column, width=canvas_width, height=44, highlightthickness=0,
                background=PLAYER_PANEL_BACKGROUND,
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
            ttk.Label(column, text=color, foreground=MUTED_TEXT_COLOR, style="Player.TLabel").pack()

        ttk.Label(self.panel, text=f"{sum(player.gems.values())} gems", justify="right", style="Player.TLabel").pack(side="right")
