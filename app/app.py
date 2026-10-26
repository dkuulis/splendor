"""Assemble the game UI components."""

from tkinter import StringVar, messagebox, ttk

from game.initialize import create_initial_state
from ai import STRATEGIES

from .bank_panel import BankPanel
from .log import Log
from .header import Header
from .market_panel import MarketPanel
from .player_panel import PlayerPanel
from .styles import configure_styles


class App:
    def __init__(self, root, state):
        self.state = state
        self.root = root
        self.control = StringVar(master=root, value="Manual")
        self.strategy = None
        self.pending_ai = None
        root.bind("<Destroy>", self.on_destroy, add="+")
        configure_styles(root)
        root.title("Splendour")
        self.shell = ttk.Frame(root, padding=20)
        self.shell.pack(fill="both", expand=True)
        self.create_ui()
        self.size_window(root)

    def create_ui(self):
        state = self.state
        shell = self.shell
        body = ttk.Frame(shell)
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=1)
        body.rowconfigure(0, weight=1)
        self.field = ttk.Frame(body)
        self.field.grid(row=0, column=0, sticky="nsew")
        sidebar = ttk.Frame(body)
        sidebar.grid(row=0, column=1, sticky="nsew", padx=(16, 0))
        self.header = Header(sidebar, self.new_game, self.control,
                             ("Manual", *STRATEGIES), self.change_control)
        self.header.pack(fill="x", padx=10, pady=(0, 12))
        self.log = Log(sidebar, state.log)
        self.log.pack(fill="both", expand=True)

        self.refresh()

    def refresh(self):
        self.cancel_ai()
        state = self.state
        field = self.field
        for child in field.winfo_children():
            child.destroy()
        self.computer = PlayerPanel(field, state.players[1], self.player_subtitle(state.players[1]),
                                    active=state.player_status(state.players[1]) == "active")
        self.computer.pack(fill="x")
        self.market = MarketPanel(field, state.market, state.decks, self.buy_card,
                                  lambda card: self.manual_turn and state.can_buy(card))
        self.market.pack(pady=10)
        self.bank = BankPanel(
            field, state.bank, self.pass_turn, self.take_gems,
            enabled=self.manual_turn,
            disabled_text="Game over" if state.turn.finished else "Computer is playing…",
            max_take=state.max_take,
        )
        self.bank.pack(fill="x", pady=(0, 10))
        self.player = PlayerPanel(field, state.players[0], self.player_subtitle(state.players[0]),
                                  active=state.player_status(state.players[0]) == "active")
        self.player.pack(fill="x")

        self.log.refresh()
        if self.ai_turn:
            self.pending_ai = self.root.after(500, self.run_ai)

    @property
    def ai_turn(self):
        return not self.state.turn.finished and self.state.current_player.is_ai and self.strategy is not None

    @property
    def manual_turn(self):
        return not self.state.turn.finished and not self.ai_turn

    def cancel_ai(self):
        if self.pending_ai is not None:
            self.root.after_cancel(self.pending_ai)
            self.pending_ai = None

    def change_control(self):
        strategy_class = STRATEGIES.get(self.control.get())
        self.strategy = strategy_class() if strategy_class else None
        self.refresh()

    def run_ai(self):
        self.pending_ai = None
        if not self.ai_turn:
            return
        self.strategy.play_turn(self.state)
        self.refresh()

    def on_destroy(self, event):
        if event.widget is self.root:
            self.cancel_ai()

    def new_game(self):
        self.cancel_ai()
        self.state = create_initial_state()
        for child in self.shell.winfo_children():
            child.destroy()
        self.create_ui()

    def pass_turn(self):
        if not self.manual_turn:
            return
        self.state.pass_turn()
        self.refresh()

    def take_gems(self, colors):
        if not self.manual_turn:
            return
        try:
            self.state.take_gems(colors)
        except ValueError as error:
            messagebox.showinfo("Cannot take gems", str(error), parent=self.shell)
            return
        self.refresh()

    def buy_card(self, card):
        if not self.manual_turn:
            return
        try:
            self.state.buy_card(card)
        except ValueError as error:
            messagebox.showinfo("Cannot buy card", str(error), parent=self.shell)
            return
        self.refresh()

    def player_subtitle(self, player):
        status = self.state.player_status(player)
        mode = self.control.get() if self.strategy else "manual"
        if status == "active":
            return f"Computer's turn ({mode})" if player.is_ai else "Your turn"
        if status == "waiting":
            return f"Waiting ({mode})" if player.is_ai else "Waiting"
        return {"draw": "Draw", "winner": "Winner", "lost": "Game over"}[status]

    def size_window(self, root):
        # Measure the complete layout using the current platform's fonts and
        # widget sizes, including the log, before setting window bounds.
        root.update_idletasks()
        width = max(1100, root.winfo_reqwidth())
        height = root.winfo_reqheight()
        root.minsize(width, height)
        root.geometry(f"{width}x{height}")
