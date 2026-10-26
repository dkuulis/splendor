import tkinter as tk
from tkinter import ttk

from game.constants import COLORS

from .drawing import draw_gem, row_centers
from .styles import (
    CARD_DETAIL_FONT,
    PALETTE,
    POINTS_FONT,
    TEXT_PALETTE,
)

COST_GEM_RADIUS = 16
COST_GEM_GAP = 8
COST_GEM_SPACING = COST_GEM_RADIUS * 2 + COST_GEM_GAP
COST_ROW_HEIGHT = 38
COST_ROW_MIN_WIDTH = 160


class CardPanel(ttk.Frame):
    def __init__(self, parent, card, on_buy=None, affordable=False):
        super().__init__(parent, padding=8, relief="ridge")

        title = tk.Frame(self, bg=PALETTE[card.color])
        title.pack(fill="x")
        tk.Label(
            title,
            text=str(card.points) if card.points else "",
            bg=PALETTE[card.color],
            fg=TEXT_PALETTE[card.color],
            font=POINTS_FONT,
            anchor="nw",
            padx=10,
            pady=6,
        ).pack(side="left")
        tk.Label(
            title,
            text=card.color,
            bg=PALETTE[card.color],
            fg=TEXT_PALETTE[card.color],
            font=CARD_DETAIL_FONT,
            padx=6,
        ).pack(side="right")

        costs = [(color, card.cost[color]) for color in COLORS if card.cost.get(color, 0)]
        cost_row = tk.Canvas(
            self, height=COST_ROW_HEIGHT,
            width=max(COST_ROW_MIN_WIDTH, len(costs) * COST_GEM_SPACING), highlightthickness=0,
            background=parent.winfo_toplevel().cget("background"),
        )
        cost_row.pack(fill="x", pady=(6, 0))
        y = COST_ROW_HEIGHT / 2
        centers = row_centers(len(costs), len(costs) * COST_GEM_SPACING, COST_GEM_SPACING)
        for x, (color, amount) in zip(centers, costs):
            draw_gem(cost_row, color, x, y, COST_GEM_RADIUS)
            cost_row.create_text(
                x, y, text=str(amount),
                fill=TEXT_PALETTE[color],
                font=CARD_DETAIL_FONT,
            )

        self.buy_button = ttk.Button(
            self, text="Buy card", command=lambda: on_buy(card),
            state="normal" if on_buy and affordable else "disabled",
        )
        self.buy_button.pack(fill="x", side="bottom", pady=(6, 0))
