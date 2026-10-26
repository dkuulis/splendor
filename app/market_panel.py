import tkinter as tk
from tkinter import ttk

from .styles import (
    CARD_DETAIL_FONT,
    DECK_LABEL_FONT,
    DECK_PALETTE,
    DECK_SYMBOL_FONT,
    DECK_TEXT_COLOR,
    OUTLINE_PALETTE,
    PALETTE,
    POINTS_FONT,
    TEXT_PALETTE,
)


class MarketPanel(ttk.Frame):
    def __init__(self, parent, market, decks):
        super().__init__(parent)
        self.market = market
        self.decks = decks

        for row, tier in enumerate((3, 2, 1)):
            self.rowconfigure(row, weight=1, uniform="rows")
            deck = tk.Frame(self, bg=DECK_PALETTE[tier], padx=12, pady=12)
            deck.grid(row=row, column=0, sticky="nsew", padx=(0, 8), pady=4)
            tk.Label(deck, text=f"LEVEL {tier}", bg=DECK_PALETTE[tier], fg=DECK_TEXT_COLOR, font=DECK_LABEL_FONT).pack()
            tk.Label(deck, text="◆" * tier, bg=DECK_PALETTE[tier], fg=DECK_TEXT_COLOR, font=DECK_SYMBOL_FONT).pack(expand=True)
            tk.Label(deck, text=f"{len(self.decks[tier])} cards", bg=DECK_PALETTE[tier], fg=DECK_TEXT_COLOR).pack(pady=5)

            for slot, card in enumerate(self.market[tier]):
                self.columnconfigure(slot + 1, weight=1, uniform="cards")
                box = ttk.Frame(self, padding=8, relief="ridge")
                box.grid(row=row, column=slot + 1, sticky="nsew", padx=4, pady=4)

                title = tk.Frame(box, bg=PALETTE[card.color])
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
                    box, height=38, width=max(160, len(costs) * 40), highlightthickness=0,
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

                ttk.Button(box, text="Buy card", state="disabled").pack(fill="x", side="bottom", pady=(6, 0))
