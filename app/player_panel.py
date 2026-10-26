import tkinter as tk
from tkinter import ttk

from game.constants import COLORS

from .player_column import PlayerColumn

from .styles import (
    ACTIVE_PLAYER_BORDER,
    PLAYER_PANEL_BACKGROUND,
    POINTS_FONT,
)


class PlayerPanel(tk.Frame):
    def __init__(self, parent, player, subtitle, active=False):
        discounts = player.discounts
        border = ACTIVE_PLAYER_BORDER if active else PLAYER_PANEL_BACKGROUND
        super().__init__(parent, background=PLAYER_PANEL_BACKGROUND, highlightthickness=2,
                         highlightbackground=border, highlightcolor=border, borderwidth=0)
        self.panel = ttk.LabelFrame(self, text=f"{player.name}  •  {subtitle}", padding=10, style="Player.TLabelframe")
        self.panel.pack(fill="both", expand=True)
        ttk.Label(self.panel, text=str(player.points), font=POINTS_FONT, style="Player.TLabel").pack(side="left", padx=(0, 20))

        self.columns = {}
        for color in COLORS:
            column = PlayerColumn(self.panel, color, discounts.get(color, 0), player.gems.get(color, 0))
            column.pack(side="left", expand=True, fill="x")
            self.columns[color] = column

        ttk.Label(self.panel, text=f"{sum(player.gems.values())} gems", justify="right", style="Player.TLabel").pack(side="right")
