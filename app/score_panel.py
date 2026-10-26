import tkinter as tk
from tkinter import font

from .styles import POINTS_FONT, TABLE_BACKGROUND, TEXT_COLOR


class ScorePanel(tk.Canvas):
    def __init__(self, parent, players):
        self.points_font = font.Font(root=parent, font=POINTS_FONT)
        self.row_height = self.points_font.metrics("linespace") + 4
        self.name_width = max(self.points_font.measure(player.name) for player in players)
        super().__init__(parent, height=self.row_height * len(players),
                         background=TABLE_BACKGROUND, borderwidth=0, highlightthickness=0)
        self.scores = []
        for row, player in enumerate(players):
            y = row * self.row_height + 2
            self.create_text(0, y, text=player.name, font=self.points_font,
                             fill=TEXT_COLOR, anchor="nw")
            self.scores.append(self.create_text(0, y, font=self.points_font,
                                                fill=TEXT_COLOR, anchor="ne"))
        self.bind("<Configure>", self.position_scores)
        self.refresh(players)

    def position_scores(self, event):
        for row, score in enumerate(self.scores):
            self.coords(score, event.width - 2, row * self.row_height + 2)

    def refresh(self, players):
        score_width = max(self.points_font.measure(str(player.points)) for player in players)
        self.configure(width=self.name_width + 12 + score_width + 4)
        for player, score in zip(players, self.scores):
            self.itemconfigure(score, text=str(player.points))
