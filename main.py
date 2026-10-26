"""Tkinter layout prototype for a two-player Splendour game."""
import sys
import tkinter as tk
from tkinter import ttk

COLORS = ("Diamond", "Sapphire", "Emerald", "Ruby", "Onyx")
PALETTE = {"Diamond": "#e5e7eb", "Sapphire": "#2563eb", "Emerald": "#15803d", "Ruby": "#be123c", "Onyx": "#334155"}


class App:
    def __init__(self, root):
        root.title("Splendour • Layout preview")
        root.geometry("1100x820")
        root.minsize(1000, 780)
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
            deck = ttk.LabelFrame(market, text=f"LEVEL {tier}", padding=12)
            deck.grid(row=row, column=0, sticky="nsew", padx=(0, 8), pady=4)
            ttk.Label(deck, text="DECK", font=("Helvetica", 12, "bold")).pack(expand=True)
            ttk.Label(deck, text="16 cards").pack(pady=5)
            for slot in range(4):
                market.columnconfigure(slot + 1, weight=1, uniform="cards")
                bonus = COLORS[(slot + tier) % 5]
                box = ttk.Frame(market, padding=8, relief="ridge")
                box.grid(row=row, column=slot + 1, sticky="nsew", padx=4, pady=4)
                tk.Label(box, text=f"{bonus}   +{(0, 2, 4)[tier - 1]} pts", bg=PALETTE[bonus], fg="#111827" if bonus == "Diamond" else "white", font=("Helvetica", 13, "bold"), pady=8).pack(fill="x")
                ttk.Label(box, text=f"Bonus: +1 {bonus}").pack(anchor="w", pady=(6, 2))
                cost = f"{tier + 1} {COLORS[(slot + 1) % 5]} · {tier} {COLORS[(slot + 2) % 5]}"
                ttk.Label(box, text="Cost: " + cost, wraplength=180).pack(anchor="w")
                ttk.Button(box, text="Buy card", state="disabled").pack(fill="x", side="bottom", pady=(6, 0))

        bank = ttk.LabelFrame(shell, text="GEM BANK", padding=10)
        bank.pack(fill="x", pady=(0, 10))
        self.selected = {}
        self.selection_text = tk.StringVar(value="Select up to 3 different gems")
        for color in COLORS:
            column = ttk.Frame(bank)
            column.pack(side="left", expand=True, fill="x", padx=8)
            tk.Label(column, text="●", fg=PALETTE[color] if color != "Diamond" else "#94a3b8", font=("Helvetica", 24)).pack()
            variable = tk.BooleanVar()
            self.selected[color] = variable
            ttk.Checkbutton(column, text=f"{color} • 4", variable=variable, command=self.update_selection).pack()

        self.player_panel(shell, "YOU", "Your turn", (0, 1, 2, 0, 1), (1, 0, 0, 1, 0), 0)
        actions = ttk.Frame(shell)
        actions.pack(fill="x", pady=(12, 0))
        ttk.Label(actions, textvariable=self.selection_text).pack(side="left")
        ttk.Button(actions, text="Take selected gems", state="disabled").pack(side="right")
        ttk.Button(actions, text="Pass", state="disabled").pack(side="right", padx=8)
        ttk.Label(shell, text="ACTIVITY   •   A new game will appear here once gameplay is connected.", foreground="#64748b").pack(anchor="w", pady=(14, 0))

    def player_panel(self, parent, name, subtitle, gems, discounts, points):
        panel = ttk.LabelFrame(parent, text=f"{name}  •  {subtitle}  •  {points} / 15 points", padding=10)
        panel.pack(fill="x")
        for i, color in enumerate(COLORS):
            column = ttk.Frame(panel)
            column.pack(side="left", expand=True, fill="x")
            ttk.Label(column, text=color, font=("Helvetica", 12, "bold")).pack(anchor="w")
            ttk.Label(column, text=f"{gems[i]} gems  /  {discounts[i]} bonus").pack(anchor="w")
        ttk.Label(panel, text=f"Gems held\n{sum(gems)} / 10", justify="right").pack(side="right")

    def update_selection(self):
        selected = [color for color, variable in self.selected.items() if variable.get()]
        self.selection_text.set(
            "Choose no more than 3 colors" if len(selected) > 3
            else "Selected: " + ", ".join(selected) if selected
            else "Select up to 3 different gems"
        )


def main():
    if sys.platform == "darwin" and tk.TkVersion < 8.6:
        raise SystemExit("Use the Homebrew Python environment in README.md; macOS requires Tk 8.6 or newer.")
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
