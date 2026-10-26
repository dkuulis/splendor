"""Assemble the game UI components."""

from tkinter import ttk

from game.initialize import create_initial_state
from game.selection import Selection

from .supply_panel import SupplyPanel
from .background import Background
from .divider_panel import DividerPanel
from .market_panel import MarketPanel
from .nobles_panel import NoblesPanel
from .player_panel import PlayerPanel
from .selection_panel import SelectionPanel
from .styles import MARKET_CARD_HEIGHT, MARKET_ROW_PADDING, WINDOW_MIN_WIDTH, configure_styles


AI_DELAY_MS = 500


class App:
    def __init__(self, root, state, strategy):
        self.root = root
        self.state = state
        self.selection = Selection()
        self.strategy = strategy
        self.state.players[1].is_ai = strategy is not None

        self.pending_ai = None

        root.title("Splendor")
        root.bind("<Destroy>", self.on_destroy, add="+")
        configure_styles(root)

        self.create_ui()

        self.background = Background(root)

    def create_ui(self):
        self.create_panels()
        self.assemble_panels()
        self.refresh()

    def create_panels(self):
        self.field = ttk.Frame(self.root)
        self.table = ttk.Frame(self.field)

        can_select_card = lambda card: self.selection.can_select_card(card, self.state)
        can_return_token = lambda token: self.selection.can_select_return_token(token, self.state)
        self.computer = PlayerPanel(self.field, on_select=self.select_card,
                                    can_select=can_select_card, on_token=self.select_return_token,
                                    can_select_token=can_return_token)
        self.computer_divider = DividerPanel(self.field)

        self.nobles = NoblesPanel(self.table)
        self.market = MarketPanel(self.table, self.select_card, lambda card: self.state.can_buy(card))
        self.supply = SupplyPanel(
            self.table, self.select_token,
            lambda token: self.selection.can_select_token(token, self.state))

        self.selection_panel = SelectionPanel(
            self.table, self.perform_action, self.select_card, self.deselect_token, self.new_game,
        )

        self.player_divider = DividerPanel(self.field)
        self.player = PlayerPanel(self.field, on_select=self.select_card,
                                 can_select=can_select_card, on_token=self.select_return_token,
                                 can_select_token=can_return_token)

    def assemble_panels(self):
        self.field.configure(padding=20)
        self.field.pack(fill="both", expand=True)

        self.computer.pack(fill="x")
        self.computer_divider.pack(fill="x")

        for row in range(3):
            self.table.rowconfigure(row, minsize=MARKET_CARD_HEIGHT + 2 * MARKET_ROW_PADDING)
        self.table.pack(pady=4)

        self.nobles.grid(row=0, column=0, rowspan=3, padx=(0, 12))
        self.supply.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=(0, 12))
        self.selection_panel.grid(row=2, column=1, sticky="ew", padx=(0, 12), pady=MARKET_ROW_PADDING)
        self.market.grid(row=0, column=2, rowspan=3, sticky="n")

        self.player_divider.pack(fill="x")
        self.player.pack(fill="x")

    def refresh(self):
        self.cancel_ai()
        state = self.state
        for index, panel in enumerate((self.player, self.computer)):
            player = state.players[index]
            selected = (self.selection.tokens if self.selection.returning
                        and index == state.turn.active_player else {})
            panel.refresh(player, state.is_active_player(player), self.manual_turn,
                          self.selection.card, selected)
        for index, divider in enumerate((self.player_divider, self.computer_divider)):
            winner = state.turn.finished and state.turn.winner == index
            active = winner if state.turn.finished else state.is_active_player(state.players[index])
            divider.refresh(active, state.players[index].points, winner)
        self.market.refresh(state.market, state.decks, self.selection.card,
                            enabled=self.manual_turn and not state.return_required)
        self.nobles.refresh(state.nobles)
        self.refresh_supply_selection()
        self.selection_panel.refresh(state, self.selection, enabled=self.manual_turn)
        self.size_window(self.root)
        if self.ai_turn:
            self.pending_ai = self.root.after(AI_DELAY_MS, self.perform_ai_selection)

    def refresh_selection(self):
        self.refresh_supply_selection()
        self.market.refresh_selection(self.selection.card)
        self.refresh_player_selection()
        self.selection_panel.refresh(self.state, self.selection, enabled=self.manual_turn)

    def refresh_supply_selection(self):
        selected = {} if self.selection.returning else self.selection.tokens
        self.supply.refresh(self.state.supply, selected,
                            enabled=self.manual_turn and not self.state.return_required)

    def refresh_player_selection(self):
        for index, panel in enumerate((self.player, self.computer)):
            selected = (self.selection.tokens if self.selection.returning
                        and index == self.state.turn.active_player else {})
            panel.refresh_selection(self.selection.card, selected)

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

    def perform_ai_selection(self):
        self.pending_ai = None
        if not self.ai_turn:
            return
        self.strategy.make_selection(self.state, self.selection)
        self.refresh_selection()
        self.pending_ai = self.root.after(AI_DELAY_MS, self.perform_ai_action)

    def perform_ai_action(self):
        self.pending_ai = None
        if not self.ai_turn:
            return
        self.selection.perform_action(self.state)
        self.refresh()

    def on_destroy(self, event):
        if event.widget is self.root:
            self.cancel_ai()

    def new_game(self):
        self.cancel_ai()
        self.state = create_initial_state()
        self.state.players[1].is_ai = self.strategy is not None
        self.selection = Selection()
        self.refresh()

    def select_card(self, card):
        if self.manual_turn:
            self.selection.select_card(card, self.state)
            self.refresh_selection()

    def select_token(self, token):
        if self.manual_turn:
            self.selection.select_token(token, self.state)
            self.refresh_selection()

    def deselect_token(self, token):
        if self.manual_turn:
            self.selection.deselect_token(token, self.state)
            self.refresh_selection()

    def select_return_token(self, token):
        if self.manual_turn:
            self.selection.select_return_token(token, self.state)
            self.refresh_selection()

    def perform_action(self):
        if not self.manual_turn:
            return
        self.selection.perform_action(self.state)
        self.refresh()

    def size_window(self, root):
        # Measure the complete layout using the current platform's fonts and
        # widget sizes before setting window bounds.
        root.update_idletasks()
        width = max(WINDOW_MIN_WIDTH, root.winfo_reqwidth())
        height = root.winfo_reqheight()
        root.minsize(width, height)
        root.geometry(f"{max(width, root.winfo_width())}x{max(height, root.winfo_height())}")
