import tkinter as tk
from tkinter import ttk

from game.constants import COLORS

from .drawing import draw_gem
from .styles import (
    CARD_DETAIL_FONT,
    COST_GEM_RADIUS,
    COST_GEM_SPACING,
    MARKET_CARD_WIDTH,
    MARKET_CARD_HEIGHT,
    PALETTE,
    POINTS_FONT,
    TEXT_PALETTE,
)


class CardPanel(ttk.Frame):
    def __init__(self, parent, card, on_buy=None, affordable=False):
        super().__init__(parent, width=MARKET_CARD_WIDTH, height=MARKET_CARD_HEIGHT,
                         padding=6, relief="ridge")
        self.pack_propagate(False)

        title = tk.Frame(self, bg=PALETTE[card.color])
        title.pack(fill="x")
        tk.Label(
            title,
            text=str(card.points) if card.points else "",
            bg=PALETTE[card.color],
            fg=TEXT_PALETTE[card.color],
            font=POINTS_FONT,
            anchor="nw",
            padx=4,
            pady=4,
        ).pack(side="left")
        tk.Label(
            title,
            text=card.color,
            bg=PALETTE[card.color],
            fg=TEXT_PALETTE[card.color],
            font=CARD_DETAIL_FONT,
            padx=4,
        ).pack(side="right")

        costs = [(color, card.cost[color]) for color in COLORS if card.cost.get(color, 0)]
        body = ttk.Frame(self)
        body.pack(fill="both", expand=True, pady=(4, 0))
        cost_column = tk.Canvas(
            body, height=len(costs) * COST_GEM_SPACING,
            width=COST_GEM_SPACING, highlightthickness=0,
            background=parent.winfo_toplevel().cget("background"),
        )
        cost_column.pack(side="left", anchor="s")
        x = COST_GEM_SPACING / 2
        for index, (color, amount) in enumerate(costs):
            y = (index + 0.5) * COST_GEM_SPACING
            draw_gem(cost_column, color, x, y, COST_GEM_RADIUS)
            cost_column.create_text(
                x, y, text=str(amount),
                fill=TEXT_PALETTE[color],
                font=CARD_DETAIL_FONT,
            )

        self.buy_button = ttk.Button(
            body, text="Buy card", width=7, command=lambda: on_buy(card),
            state="normal" if on_buy and affordable else "disabled",
        )
        self.buy_button.pack(side="right", anchor="s")
