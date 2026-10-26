from tkinter import ttk

from .styles import (
    SUBTITLE_FONT,
    TITLE_FONT,
)


class Header(ttk.Frame):
    def __init__(self, parent, state):
        super().__init__(parent)
        self.state = state
        header = ttk.Frame(self)
        header.pack(fill="x")
        ttk.Label(header, text="SPLENDOUR", font=TITLE_FONT).pack(side="left")
        ttk.Label(header, text="  vs  ".join(player.name for player in self.state.players), font=SUBTITLE_FONT).pack(side="left", padx=24)
        ttk.Button(header, text="New game", state="disabled").pack(side="right")
        ttk.Button(header, text="Rules", state="disabled").pack(side="right", padx=8)

        ttk.Label(self, text="Layout preview • Sample cards and balances • Gameplay coming next").pack(anchor="w", pady=(8, 14))
