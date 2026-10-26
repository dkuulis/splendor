"""Tkinter layout prototype for a two-player Splendour game."""

import tkinter as tk
from tkinter import ttk

from game.constants import COLORS
from game.preview import create_preview_state

PALETTE = {"Diamond": "#e5e7eb", "Sapphire": "#2563eb", "Emerald": "#15803d", "Ruby": "#be123c", "Onyx": "#334155"}
TEXT_PALETTE = {"Diamond": "#111827", "Sapphire": "white", "Emerald": "white", "Ruby": "white", "Onyx": "white"}
OUTLINE_PALETTE = {**PALETTE, "Diamond": "#94a3b8"}
DECK_PALETTE = {1: "#166534", 2: "#a16207", 3: "#1e40af"}
MUTED_TEXT_COLOR = "#64748b"
DECK_TEXT_COLOR = "white"
SELECTION_OUTLINE_COLOR = "#f59e0b"

TITLE_FONT = ("Helvetica", 24, "bold")
SUBTITLE_FONT = ("Helvetica", 12)
DECK_LABEL_FONT = ("Helvetica", 11, "bold")
DECK_SYMBOL_FONT = ("Helvetica", 16, "bold")
POINTS_FONT = ("Helvetica", 28, "bold")
CARD_DETAIL_FONT = ("Helvetica", 13, "bold")
SELECTION_MARKER_FONT = ("Helvetica", 20, "bold")


class App:
    def __init__(self, root, state):
        self.state = state
        root.title("Splendour • Layout preview")
        shell = ttk.Frame(root, padding=20)
        shell.pack(fill="both", expand=True)

        self.create_header(shell)
        self.create_player_panel(shell, 1)
        self.create_market(shell)
        self.create_gem_bank(shell)
        self.create_player_panel(shell, 0)
        self.create_footer(shell)

        self.size_window(root)

    def size_window(self, root):
        # Measure the complete layout using the current platform's fonts and
        # widget sizes, including the footer, before setting window bounds.
        root.update_idletasks()
        width = max(1100, root.winfo_reqwidth())
        height = root.winfo_reqheight()
        root.minsize(width, height)
        root.geometry(f"{width}x{height}")

    def create_header(self, parent):
        header = ttk.Frame(parent)
        header.pack(fill="x")
        ttk.Label(header, text="SPLENDOUR", font=TITLE_FONT).pack(side="left")
        ttk.Label(header, text="  vs  ".join(player.name for player in self.state.players), font=SUBTITLE_FONT).pack(side="left", padx=24)
        ttk.Button(header, text="New game", state="disabled").pack(side="right")
        ttk.Button(header, text="Rules", state="disabled").pack(side="right", padx=8)

        ttk.Label(parent, text="Layout preview • Sample cards and balances • Gameplay coming next").pack(anchor="w", pady=(8, 14))

    def create_footer(self, parent):
        actions = ttk.Frame(parent)
        actions.pack(fill="x", pady=(12, 0))
        ttk.Label(actions, textvariable=self.selection_text).pack(side="left")
        ttk.Button(actions, text="Take selected gems", state="disabled").pack(side="right")
        ttk.Button(actions, text="Pass", state="disabled").pack(side="right", padx=8)

        ttk.Label(parent, text="ACTIVITY   •   A new game will appear here once gameplay is connected.", foreground=MUTED_TEXT_COLOR).pack(anchor="w", pady=(14, 0))

    def create_market(self, parent):
        market = ttk.Frame(parent)
        market.pack(fill="both", expand=True, pady=10)

        for row, tier in enumerate((3, 2, 1)):
            market.rowconfigure(row, weight=1, uniform="rows")
            deck = tk.Frame(market, bg=DECK_PALETTE[tier], padx=12, pady=12)
            deck.grid(row=row, column=0, sticky="nsew", padx=(0, 8), pady=4)
            tk.Label(deck, text=f"LEVEL {tier}", bg=DECK_PALETTE[tier], fg=DECK_TEXT_COLOR, font=DECK_LABEL_FONT).pack()
            tk.Label(deck, text="◆" * tier, bg=DECK_PALETTE[tier], fg=DECK_TEXT_COLOR, font=DECK_SYMBOL_FONT).pack(expand=True)
            tk.Label(deck, text=f"{len(self.state.decks[tier])} cards", bg=DECK_PALETTE[tier], fg=DECK_TEXT_COLOR).pack(pady=5)

            for slot, card in enumerate(self.state.market[tier]):
                market.columnconfigure(slot + 1, weight=1, uniform="cards")
                box = ttk.Frame(market, padding=8, relief="ridge")
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

    def create_gem_bank(self, parent):
        bank = ttk.Frame(parent, padding=10)
        bank.pack(fill="x", pady=(0, 10))

        self.selected = {}
        self.gem_stacks = {}
        self.selection_text = tk.StringVar(value="Click gems to cycle selection: 0 / 1 / 2")

        for color in COLORS:
            available = self.state.bank.get(color, 0)
            column = ttk.Frame(bank)
            column.pack(side="left", expand=True, fill="x", padx=8)
            variable = tk.IntVar(value=0)
            self.selected[color] = variable

            tokens = tk.Canvas(
                column, width=176, height=48, highlightthickness=0,
                background=parent.winfo_toplevel().cget("background"),
            )
            tokens.pack()

            start = (176 - available * 42) / 2
            gem_items = []
            for token in range(available):
                x = start + token * 42
                gem = tokens.create_oval(
                    x + 2, 5, x + 40, 43,
                    fill=PALETTE[color],
                    outline=OUTLINE_PALETTE[color],
                    width=2,
                    tags=("gem",),
                )
                marker = tokens.create_text(
                    x + 21, 24, text="✓",
                    fill=TEXT_PALETTE[color],
                    font=SELECTION_MARKER_FONT,
                    state="hidden", tags=("gem",),
                )
                gem_items.append((gem, marker))

            self.gem_stacks[color] = (tokens, gem_items)
            tokens.tag_bind("gem", "<Button-1>", lambda event, selected=variable, count=available: self.toggle_gem(selected, count))
            tokens.tag_bind("gem", "<Enter>", lambda event, canvas=tokens: canvas.configure(cursor="hand2"))
            tokens.tag_bind("gem", "<Leave>", lambda event, canvas=tokens: canvas.configure(cursor=""))
            ttk.Label(column, text=color).pack()

    def create_player_panel(self, parent, player_index):
        player = self.state.players[player_index]
        if self.state.turn.finished:
            subtitle = "Draw" if self.state.turn.winner is None else ("Winner" if self.state.turn.winner == player_index else "Game over")
        elif self.state.turn.active_player == player_index:
            subtitle = "Computer's turn" if player.is_ai else "Your turn"
        else:
            subtitle = "Rules-based AI" if player.is_ai else "Waiting"
        discounts = player.discounts
        panel = ttk.LabelFrame(parent, text=f"{player.name}  •  {subtitle}", padding=10)
        panel.pack(fill="x")
        ttk.Label(panel, text=str(player.points), font=POINTS_FONT).pack(side="left", padx=(0, 20))

        for color in COLORS:
            column = ttk.Frame(panel)
            column.pack(side="left", expand=True, fill="x")

            card_count, gem_count = discounts.get(color, 0), player.gems.get(color, 0)
            spacing = 28
            group_gap = 10 if card_count and gem_count else 0
            content_width = (card_count + gem_count) * spacing + group_gap
            canvas_width = max(100, content_width)

            resources = tk.Canvas(
                column, width=canvas_width, height=44, highlightthickness=0,
                background=parent.winfo_toplevel().cget("background"),
            )
            resources.pack()

            outline = OUTLINE_PALETTE[color]
            start = (canvas_width - content_width) / 2
            for card in range(card_count):
                x = start + card * spacing
                resources.create_rectangle(x + 2, 10, x + 26, 34, fill=PALETTE[color], outline=outline)
            for gem in range(gem_count):
                x = start + card_count * spacing + group_gap + gem * spacing
                resources.create_oval(x + 2, 10, x + 26, 34, fill=PALETTE[color], outline=outline)
            ttk.Label(column, text=color, foreground=MUTED_TEXT_COLOR).pack()

        ttk.Label(panel, text=f"{sum(player.gems.values())} gems", justify="right").pack(side="right")

    def toggle_gem(self, selected, available):
        selected.set((selected.get() + 1) % (min(2, available) + 1))
        self.update_selection()

    def update_selection(self):
        for color, variable in self.selected.items():
            canvas, gem_items = self.gem_stacks[color]
            for index, (gem, marker) in enumerate(gem_items):
                selected = index < variable.get()
                canvas.itemconfigure(
                    gem,
                    outline=SELECTION_OUTLINE_COLOR if selected else OUTLINE_PALETTE[color],
                    width=4 if selected else 2,
                )
                canvas.itemconfigure(marker, state="normal" if selected else "hidden")

        selected = [f"{variable.get()} {color}" for color, variable in self.selected.items() if variable.get()]
        self.selection_text.set(
            "Selected: " + ", ".join(selected) if selected
            else "Click gems to cycle selection: 0 / 1 / 2"
        )


def main():
    root = tk.Tk()
    App(root, create_preview_state())
    root.mainloop()


if __name__ == "__main__":
    main()
