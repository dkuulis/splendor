import tkinter as tk
from tkinter import ttk

from game.constants import COLORS

from .drawing import draw_gem
from .styles import (
    CARD_DETAIL_FONT,
    COST_GEM_RADIUS,
    COST_GEM_SPACING,
    DISABLED_CARD_BORDER,
    DISABLED_PALETTE,
    MARKET_CARD_WIDTH,
    MARKET_CARD_HEIGHT,
    OUTLINE_PALETTE,
    PALETTE,
    POINTS_FONT,
    TEXT_PALETTE,
)


class CardPanel(tk.Frame):
    def __init__(self, parent, card, on_buy=None, affordable=False):
        enabled = bool(on_buy and affordable)
        palette = PALETTE if enabled else DISABLED_PALETTE
        border = OUTLINE_PALETTE[card.color] if enabled else DISABLED_CARD_BORDER
        super().__init__(parent, width=MARKET_CARD_WIDTH, height=MARKET_CARD_HEIGHT,
                         padx=6, pady=6, highlightthickness=1,
                         highlightbackground=border, highlightcolor=border)
        self.pack_propagate(False)

        title = tk.Frame(self, bg=palette[card.color])
        title.pack(fill="x")
        tk.Label(
            title,
            text=str(card.points) if card.points else "",
            bg=palette[card.color],
            fg=TEXT_PALETTE[card.color],
            font=POINTS_FONT,
            anchor="nw",
            padx=4,
            pady=4,
        ).pack(side="left")
        tk.Label(
            title,
            text=card.color,
            bg=palette[card.color],
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

        if enabled:
            widgets = [self]
            while widgets:
                widget = widgets.pop()
                widget.configure(cursor="hand2")
                widget.bind("<Button-1>", lambda event: on_buy(card))
                widgets.extend(widget.winfo_children())
