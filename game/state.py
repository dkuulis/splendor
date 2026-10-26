from .constants import COLORS
from .player import Player
from .turn import Turn


class State:
    """Game state and legal turn transitions."""

    def __init__(self):
        self.players = [Player("YOU"), Player("COMPUTER", is_ai=True)]
        self.bank = dict.fromkeys(COLORS, 4)
        # Every tier is always present; no cards means an empty list, not None.
        self.decks = {tier: [] for tier in (1, 2, 3)}
        self.market = {tier: [] for tier in (1, 2, 3)}
        self.turn = Turn()
        self.log = []
        self.target_points = 15
        self.gem_limit = 10

    def pass_turn(self):
        if self.turn.finished:
            raise ValueError("The game has already ended.")
        self.log.append(f"{self.players[self.turn.active_player].name} passed.")
        self.turn.consecutive_passes += 1
        if self.players[self.turn.active_player].points >= self.target_points:
            self.turn.final_round = True
        round_complete = self.turn.active_player == len(self.players) - 1
        if self.turn.consecutive_passes >= 2 or (self.turn.final_round and round_complete):
            self.turn.finished = True
            scores = [(player.points, -len(player.cards)) for player in self.players]
            best = max(scores)
            winners = [index for index, score in enumerate(scores) if score == best]
            self.turn.winner = winners[0] if len(winners) == 1 else None
            result = "Draw." if self.turn.winner is None else f"{self.players[self.turn.winner].name} wins."
            reason = "Two consecutive passes." if self.turn.consecutive_passes >= 2 else "Final round complete."
            self.log.append(f"Game over: {reason} {result}")
        else:
            self.turn.active_player = (self.turn.active_player + 1) % len(self.players)
            if round_complete:
                self.turn.round_number += 1

    def player_status(self, player):
        """Return a player's game status without UI-specific wording."""
        player_index = self.players.index(player)
        if self.turn.finished:
            if self.turn.winner is None:
                return "draw"
            return "winner" if self.turn.winner == player_index else "lost"
        return "active" if self.turn.active_player == player_index else "waiting"
