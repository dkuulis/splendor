"""Tkinter layout prototype for a two-player Splendour game."""
import sys
import tkinter as tk
from tkinter import ttk

COLORS = ("Diamond", "Sapphire", "Emerald", "Ruby", "Onyx")
PALETTE = {"Diamond": "#e5e7eb", "Sapphire": "#2563eb", "Emerald": "#15803d", "Ruby": "#be123c", "Onyx": "#334155"}
DECK_PALETTE = {1: "#166534", 2: "#a16207", 3: "#1e40af"}


class App:
    def __init__(self, root):
        root.title("Splendour • Layout preview")
        shell = ttk.Frame(root, padding=20)
        shell.pack(fill="both", expand=True)

        header = ttk.Frame(shell)
        header.pack(fill="x")
        ttk.Label(header, text="SPLENDOUR", font=("Helvetica", 24, "bold")).pack(side="left")
        ttk.Label(header, text="YOU  vs  COMPUTER", font=("Helvetica", 12)).pack(side="left", padx=24)
        ttk.Button(header, text="New game", state="disabled").pack(side="right")
        ttk.Button(header, text="Rules", state="disabled").pack(side="right", padx=8)
        ttk.Label(shell, text="Layout preview • Sample cards and balances • Gameplay coming next").pack(anchor="w", pady=(8, 14))

        self.player_panel(shell, "COMPUTER", "Rules-based AI", (1, 2, 0, 1, 0), (0, 1, 0, 0, 1), 2)

        market = ttk.Frame(shell)
        market.pack(fill="both", expand=True, pady=10)
        for row, tier in enumerate((3, 2, 1)):
            market.rowconfigure(row, weight=1, uniform="rows")
            deck = tk.Frame(market, bg=DECK_PALETTE[tier], padx=12, pady=12)
            deck.grid(row=row, column=0, sticky="nsew", padx=(0, 8), pady=4)
            tk.Label(deck, text=f"LEVEL {tier}", bg=DECK_PALETTE[tier], fg="white", font=("Helvetica", 11, "bold")).pack()
            tk.Label(deck, text="◆" * tier, bg=DECK_PALETTE[tier], fg="white", font=("Helvetica", 16, "bold")).pack(expand=True)
            tk.Label(deck, text="16 cards", bg=DECK_PALETTE[tier], fg="white").pack(pady=5)
            for slot in range(4):
                market.columnconfigure(slot + 1, weight=1, uniform="cards")
                bonus = COLORS[(slot + tier) % 5]
                box = ttk.Frame(market, padding=8, relief="ridge")
                box.grid(row=row, column=slot + 1, sticky="nsew", padx=4, pady=4)
                title = tk.Frame(box, bg=PALETTE[bonus])
                title.pack(fill="x")
                tk.Label(
                    title,
                    text=str((0, 2, 4)[tier - 1]) if tier > 1 else "",
                    bg=PALETTE[bonus],
                    fg="#111827" if bonus == "Diamond" else "white",
                    font=("Helvetica", 28, "bold"),
                    anchor="nw",
                    padx=10,
                    pady=6,
                ).pack(side="left")
                tk.Label(
                    title,
                    text=bonus,
                    bg=PALETTE[bonus],
                    fg="#111827" if bonus == "Diamond" else "white",
                    font=("Helvetica", 13, "bold"),
                    padx=6,
                ).pack(side="right")
                costs = [
                    (COLORS[(slot + offset + 1) % 5], max(1, tier + 1 - offset))
                    for offset in range(4 if slot >= 2 else 2)
                ]
                cost_row = tk.Canvas(
                    box, height=38, width=160, highlightthickness=0,
                    background=root.cget("background"),
                )
                cost_row.pack(fill="x", pady=(6, 0))
                for index, (color, amount) in enumerate(costs):
                    x = 20 + index * 40
                    cost_row.create_oval(
                        x - 16, 3, x + 16, 35,
                        fill=PALETTE[color],
                        outline="#94a3b8" if color == "Diamond" else PALETTE[color],
                    )
                    cost_row.create_text(
                        x, 19, text=str(amount),
                        fill="#111827" if color == "Diamond" else "white",
                        font=("Helvetica", 13, "bold"),
                    )
                ttk.Button(box, text="Buy card", state="disabled").pack(fill="x", side="bottom", pady=(6, 0))

        bank = ttk.Frame(shell, padding=10)
        bank.pack(fill="x", pady=(0, 10))
        self.selected = {}
        self.gem_stacks = {}
        self.selection_text = tk.StringVar(value="Click gems to cycle selection: 0 / 1 / 2")
        for color, available in zip(COLORS, (4, 3, 2, 4, 1)):
            column = ttk.Frame(bank)
            column.pack(side="left", expand=True, fill="x", padx=8)
            variable = tk.IntVar(value=0)
            self.selected[color] = variable
            tokens = tk.Canvas(
                column, width=176, height=48, highlightthickness=0,
                background=root.cget("background"),
            )
            tokens.pack()
            start = (176 - available * 42) / 2
            gem_items = []
            for token in range(available):
                x = start + token * 42
                gem = tokens.create_oval(
                    x + 2, 5, x + 40, 43,
                    fill=PALETTE[color],
                    outline="#94a3b8" if color == "Diamond" else PALETTE[color],
                    width=2,
                    tags=("gem",),
                )
                marker = tokens.create_text(
                    x + 21, 24, text="✓",
                    fill="#111827" if color == "Diamond" else "white",
                    font=("Helvetica", 20, "bold"),
                    state="hidden", tags=("gem",),
                )
                gem_items.append((gem, marker))
            self.gem_stacks[color] = (tokens, gem_items)
            tokens.tag_bind("gem", "<Button-1>", lambda event, selected=variable, count=available: self.toggle_gem(selected, count))
            tokens.tag_bind("gem", "<Enter>", lambda event, canvas=tokens: canvas.configure(cursor="hand2"))
            tokens.tag_bind("gem", "<Leave>", lambda event, canvas=tokens: canvas.configure(cursor=""))
            ttk.Label(column, text=color).pack()

        self.player_panel(shell, "YOU", "Your turn", (0, 1, 2, 0, 1), (1, 0, 0, 1, 0), 0)
        actions = ttk.Frame(shell)
        actions.pack(fill="x", pady=(12, 0))
        ttk.Label(actions, textvariable=self.selection_text).pack(side="left")
        ttk.Button(actions, text="Take selected gems", state="disabled").pack(side="right")
        ttk.Button(actions, text="Pass", state="disabled").pack(side="right", padx=8)
        ttk.Label(shell, text="ACTIVITY   •   A new game will appear here once gameplay is connected.", foreground="#64748b").pack(anchor="w", pady=(14, 0))

        # Measure the complete layout using the current platform's fonts and
        # widget sizes, including the footer, before setting window bounds.
        root.update_idletasks()
        width = max(1100, root.winfo_reqwidth())
        height = root.winfo_reqheight()
        root.minsize(width, height)
        root.geometry(f"{width}x{height}")

    def player_panel(self, parent, name, subtitle, gems, discounts, points):
        panel = ttk.LabelFrame(parent, text=f"{name}  •  {subtitle}  •  {points} / 15 points", padding=10)
        panel.pack(fill="x")
        for i, color in enumerate(COLORS):
            column = ttk.Frame(panel)
            column.pack(side="left", expand=True, fill="x")
            ttk.Label(column, text=color, font=("Helvetica", 12, "bold")).pack(anchor="w")
            ttk.Label(column, text=f"{gems[i]} gems  /  {discounts[i]} bonus").pack(anchor="w")
        ttk.Label(panel, text=f"Gems held\n{sum(gems)} / 10", justify="right").pack(side="right")

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
                    outline="#f59e0b" if selected else ("#94a3b8" if color == "Diamond" else PALETTE[color]),
                    width=4 if selected else 2,
                )
                canvas.itemconfigure(marker, state="normal" if selected else "hidden")
        selected = [f"{variable.get()} {color}" for color, variable in self.selected.items() if variable.get()]
        self.selection_text.set(
            "Selected: " + ", ".join(selected) if selected
            else "Click gems to cycle selection: 0 / 1 / 2"
        )


def main():
    if sys.platform == "darwin" and tk.TkVersion < 8.6:
        raise SystemExit("Use the Homebrew Python environment in README.md; macOS requires Tk 8.6 or newer.")
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
