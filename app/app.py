"""Assemble the game UI components."""

from tkinter import messagebox, ttk

from game.initialize import create_initial_state

from .bank_panel import BankPanel
from .log import Log
from .header import Header
from .market_panel import MarketPanel
from .player_panel import PlayerPanel
from .styles import configure_styles


class App:
    def __init__(self, root, state):
        self.state = state
        configure_styles(root)
        root.title("Splendour")
        self.shell = ttk.Frame(root, padding=20)
        self.shell.pack(fill="both", expand=True)
        self.create_ui()
        self.size_window(root)

    def create_ui(self):
        state = self.state
        shell = self.shell
        self.header = Header(shell, [player.name for player in state.players], self.new_game)
        self.header.pack(fill="x")

        body = ttk.Frame(shell)
        body.pack(fill="both", expand=True, pady=(12, 0))
        body.columnconfigure(0, weight=1)
        body.rowconfigure(0, weight=1)
        self.field = ttk.Frame(body)
        self.field.grid(row=0, column=0, sticky="nsew")
        self.log = Log(body, state.log)
        self.log.grid(row=0, column=1, sticky="nsew", padx=(16, 0))

        self.refresh()

    def refresh(self):
        state = self.state
        field = self.field
        for child in field.winfo_children():
            child.destroy()
        self.computer = PlayerPanel(field, state.players[1], self.player_subtitle(state.players[1]),
                                    active=state.player_status(state.players[1]) == "active")
        self.computer.pack(fill="x")
        self.market = MarketPanel(field, state.market, state.decks, self.buy_card, state.can_buy)
        self.market.pack(fill="both", expand=True, pady=10)
        self.bank = BankPanel(
            field, state.bank, self.pass_turn, self.take_gems,
            enabled=not state.turn.finished,
            max_take=min(3, max(0, state.gem_limit - sum(state.current_player.gems.values()))),
        )
        self.bank.pack(fill="x", pady=(0, 10))
        self.player = PlayerPanel(field, state.players[0], self.player_subtitle(state.players[0]),
                                  active=state.player_status(state.players[0]) == "active")
        self.player.pack(fill="x")

        self.log.refresh()

    def new_game(self):
        self.state = create_initial_state()
        for child in self.shell.winfo_children():
            child.destroy()
        self.create_ui()

    def pass_turn(self):
        if self.state.turn.finished:
            return
        self.state.pass_turn()
        self.refresh()

    def take_gems(self, colors):
        try:
            self.state.take_gems(colors)
        except ValueError as error:
            messagebox.showinfo("Cannot take gems", str(error), parent=self.shell)
            return
        self.refresh()

    def buy_card(self, card):
        try:
            self.state.buy_card(card)
        except ValueError as error:
            messagebox.showinfo("Cannot buy card", str(error), parent=self.shell)
            return
        self.refresh()

    def player_subtitle(self, player):
        status = self.state.player_status(player)
        if status == "active":
            return "Computer's turn (manual)" if player.is_ai else "Your turn"
        if status == "waiting":
            return "Waiting (manual)" if player.is_ai else "Waiting"
        return {"draw": "Draw", "winner": "Winner", "lost": "Game over"}[status]

    def size_window(self, root):
        # Measure the complete layout using the current platform's fonts and
        # widget sizes, including the log, before setting window bounds.
        root.update_idletasks()
        width = max(1100, root.winfo_reqwidth())
        height = root.winfo_reqheight()
        root.minsize(width, height)
        root.geometry(f"{width}x{height}")
