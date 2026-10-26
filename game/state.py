from .constants import COLORS
from .player import Player
from .turn import Turn


class State:
    """Independent state containers, ready for a future deal routine."""

    def __init__(self):
        self.players = [Player("YOU"), Player("COMPUTER", is_ai=True)]
        self.bank = dict.fromkeys(COLORS, 4)
        self.decks = {tier: [] for tier in (1, 2, 3)}
        self.market = {tier: [None] * 4 for tier in (1, 2, 3)}
        self.turn = Turn()
        self.target_points = 15
        self.gem_limit = 10
