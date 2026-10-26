from tkinter import ttk

from .styles import POINTS_FONT


class ScorePanel(ttk.Frame):
    def __init__(self, parent, players):
        super().__init__(parent)
        self.players = players
        self.scores = []
        self.columnconfigure(0, weight=1)
        for row, player in enumerate(players):
            ttk.Label(self, text=player.name).grid(row=row, column=0, sticky="w", padx=(0, 12))
            score = ttk.Label(self, font=POINTS_FONT)
            score.grid(row=row, column=1, sticky="e")
            self.scores.append(score)
        self.refresh()

    def refresh(self):
        for player, score in zip(self.players, self.scores):
            score.configure(text=str(player.points))
