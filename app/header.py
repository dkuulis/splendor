from tkinter import ttk

from .styles import (
    SUBTITLE_FONT,
    TITLE_FONT,
)


class Header(ttk.Frame):
    def __init__(self, parent, state, on_new_game=None):
        super().__init__(parent)
        self.state = state
        header = ttk.Frame(self)
        header.pack(fill="x")
        ttk.Label(header, text="SPLENDOUR", font=TITLE_FONT).pack(side="left")
        ttk.Label(header, text="  vs  ".join(player.name for player in self.state.players), font=SUBTITLE_FONT).pack(side="left", padx=24)
        self.new_game_button = ttk.Button(header, text="New game", command=on_new_game, state="normal" if on_new_game else "disabled")
        self.new_game_button.pack(side="right")
        ttk.Button(header, text="Rules", state="disabled").pack(side="right", padx=8)
