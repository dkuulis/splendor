"""Assemble the game UI components."""

from tkinter import ttk

from .bank_panel import BankPanel
from .log import Log
from .header import Header
from .market_panel import MarketPanel
from .player_panel import PlayerPanel


class App:
    def __init__(self, root, state):
        self.state = state
        root.title("Splendour • Layout preview")
        shell = ttk.Frame(root, padding=20)
        shell.pack(fill="both", expand=True)

        self.header = Header(shell, state)
        self.header.pack(fill="x")

        body = ttk.Frame(shell)
        body.pack(fill="both", expand=True, pady=(12, 0))
        body.columnconfigure(0, weight=1)
        body.rowconfigure(0, weight=1)
        field = ttk.Frame(body)
        field.grid(row=0, column=0, sticky="nsew")
        self.log = Log(body)
        self.log.grid(row=0, column=1, sticky="nsew", padx=(16, 0))

        self.computer = PlayerPanel(field, state.players[1], self.player_subtitle(state.players[1]))
        self.computer.pack(fill="x")
        self.market = MarketPanel(field, state.market, state.decks)
        self.market.pack(fill="both", expand=True, pady=10)
        self.bank = BankPanel(field, state.bank)
        self.bank.pack(fill="x", pady=(0, 10))
        self.player = PlayerPanel(field, state.players[0], self.player_subtitle(state.players[0]))
        self.player.pack(fill="x")

        self.size_window(root)

    def player_subtitle(self, player):
        status = self.state.player_status(player)
        if status == "active":
            return "Computer's turn" if player.is_ai else "Your turn"
        if status == "waiting":
            return "Rules-based AI" if player.is_ai else "Waiting"
        return {"draw": "Draw", "winner": "Winner", "lost": "Game over"}[status]

    def size_window(self, root):
        # Measure the complete layout using the current platform's fonts and
        # widget sizes, including the log, before setting window bounds.
        root.update_idletasks()
        width = max(1100, root.winfo_reqwidth())
        height = root.winfo_reqheight()
        root.minsize(width, height)
        root.geometry(f"{width}x{height}")
