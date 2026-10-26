import tkinter as tk
from tkinter import ttk

from .styles import (
    CARD_DETAIL_FONT,
    OUTLINE_PALETTE,
    PALETTE,
    POINTS_FONT,
    TEXT_PALETTE,
)


class CardPanel(ttk.Frame):
    def __init__(self, parent, card):
        super().__init__(parent, padding=8, relief="ridge")
        self.card = card

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

        costs = [(color, amount) for color, amount in card.cost.items() if amount]
        cost_row = tk.Canvas(
            self, height=38, width=max(160, len(costs) * 40), highlightthickness=0,
            background=parent.winfo_toplevel().cget("background"),
        )
        cost_row.pack(fill="x", pady=(6, 0))
        for index, (color, amount) in enumerate(costs):
            x = 20 + index * 40
            cost_row.create_oval(
                x - 16, 3, x + 16, 35,
                fill=PALETTE[color],
                outline=OUTLINE_PALETTE[color],
            )
            cost_row.create_text(
                x, 19, text=str(amount),
                fill=TEXT_PALETTE[color],
                font=CARD_DETAIL_FONT,
            )

        ttk.Button(self, text="Buy card", state="disabled").pack(fill="x", side="bottom", pady=(6, 0))
