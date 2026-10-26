from .constants import COLORS
from .player import Player
from .turn import Turn


class State:
    """Independent state containers, ready for a future deal routine."""

    def __init__(self):
        self.players = [Player("YOU"), Player("COMPUTER", is_ai=True)]
        self.bank = dict.fromkeys(COLORS, 4)
        # Every tier is always present; no cards means an empty list, not None.
        self.decks = {tier: [] for tier in (1, 2, 3)}
        self.market = {tier: [] for tier in (1, 2, 3)}
        self.turn = Turn()
        self.target_points = 15
        self.gem_limit = 10

    def player_status(self, player):
        """Return a player's game status without UI-specific wording."""
        player_index = self.players.index(player)
        if self.turn.finished:
            if self.turn.winner is None:
                return "draw"
            return "winner" if self.turn.winner == player_index else "lost"
        return "active" if self.turn.active_player == player_index else "waiting"
