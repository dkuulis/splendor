"""Assemble the game UI components."""

from tkinter import messagebox, ttk

from game.initialize import create_initial_state

from .supply_panel import SupplyPanel
from .background import Background
from .divider_panel import DividerPanel
from .market_panel import MarketPanel
from .nobles_panel import NoblesPanel
from .player_panel import PlayerPanel
from .selection_panel import SelectionPanel
from .styles import MARKET_CARD_HEIGHT, MARKET_ROW_PADDING, WINDOW_MIN_WIDTH, configure_styles


class App:
    def __init__(self, root, state, strategy):
        self.state = state
        self.root = root
        self.strategy = strategy
        self.pending_ai = None
        root.bind("<Destroy>", self.on_destroy, add="+")
        configure_styles(root)
        root.title("Splendor")
        self.shell = ttk.Frame(root, padding=20)
        self.shell.pack(fill="both", expand=True)
        self.create_ui()
        self.background = Background(root)

    def create_ui(self):
        self.field = ttk.Frame(self.shell)
        self.field.pack(fill="both", expand=True)

        self.computer = PlayerPanel(self.field, on_select=self.select_card)
        self.computer.pack(fill="x")
        self.computer_divider = DividerPanel(self.field)
        self.computer_divider.pack(fill="x")
        table = ttk.Frame(self.field)
        table.pack(pady=4)
        for row in range(3):
            table.rowconfigure(row, minsize=MARKET_CARD_HEIGHT + 2 * MARKET_ROW_PADDING)
        self.nobles = NoblesPanel(table)
        self.nobles.grid(row=0, column=0, rowspan=3, padx=(0, 12))
        self.market = MarketPanel(table, self.select_card,
                                  lambda card: self.state.can_buy(card))
        self.market.grid(row=0, column=2, rowspan=3, sticky="n")
        self.supply = SupplyPanel(table, self.select_token)
        self.supply.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=(0, 12))
        self.selection = SelectionPanel(
            table, self.perform_action, self.select_card, self.deselect_token, self.new_game,
        )
        self.selection.grid(row=2, column=1, sticky="ew", padx=(0, 12), pady=MARKET_ROW_PADDING)
        self.player_divider = DividerPanel(self.field)
        self.player_divider.pack(fill="x")
        self.player = PlayerPanel(self.field, on_select=self.select_card)
        self.player.pack(fill="x")

        self.refresh()

    def refresh(self):
        self.cancel_ai()
        state = self.state
        self.computer.refresh(state.players[1], state.is_active_player(state.players[1]), self.manual_turn)
        self.player.refresh(state.players[0], state.is_active_player(state.players[0]), self.manual_turn)
        for index, divider in enumerate((self.player_divider, self.computer_divider)):
            winner = state.turn.finished and state.turn.winner == index
            active = winner if state.turn.finished else state.is_active_player(state.players[index])
            divider.refresh(active, state.players[index].points, winner)
        self.computer.refresh_selection(state.selection.card)
        self.player.refresh_selection(state.selection.card)
        self.market.refresh(state.market, state.decks, state.selection.card, enabled=self.manual_turn)
        self.nobles.refresh(state.nobles)
        self.supply.refresh(state.supply, state.selection.tokens, enabled=self.manual_turn)
        self.selection.refresh(state, enabled=self.manual_turn)
        self.size_window(self.root)
        if self.ai_turn:
            self.pending_ai = self.root.after(500, self.run_ai)

    def refresh_selection(self):
        self.supply.refresh(self.state.supply, self.state.selection.tokens, enabled=self.manual_turn)
        self.market.refresh_selection(self.state.selection.card)
        self.computer.refresh_selection(self.state.selection.card)
        self.player.refresh_selection(self.state.selection.card)
        self.selection.refresh(self.state, enabled=self.manual_turn)

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
        self.refresh()

    def select_card(self, card):
        if self.manual_turn:
            if self.state.selection.action_kind == "reserve":
                self.state.selection.reserve_card(card, self.state)
            else:
                self.state.selection.select_card(card, self.state)
            self.refresh_selection()

    def select_token(self, token):
        if self.manual_turn:
            self.state.selection.select_token(token, self.state)
            self.refresh_selection()

    def deselect_token(self, token):
        if self.manual_turn:
            self.state.selection.deselect_token(token, self.state)
            self.refresh_selection()

    def perform_action(self):
        if not self.manual_turn:
            return
        try:
            self.state.perform_action()
        except ValueError as error:
            messagebox.showinfo("Cannot perform action", str(error), parent=self.shell)
            return
        self.refresh()

    def size_window(self, root):
        # Measure the complete layout using the current platform's fonts and
        # widget sizes before setting window bounds.
        root.update_idletasks()
        width = max(WINDOW_MIN_WIDTH, root.winfo_reqwidth())
        height = root.winfo_reqheight()
        root.minsize(width, height)
        root.geometry(f"{max(width, root.winfo_width())}x{max(height, root.winfo_height())}")
