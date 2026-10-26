from .constants import TARGET_POINTS


class Turn:
    def __init__(self):
        self.active_player = 0
        self.round_number = 1
        self.consecutive_passes = 0
        self.final_round = False
        self.finished = False
        self.winner = None  # None also means a draw when finished.


def advance_turn(state):
    """Check game completion and advance to the next player when play continues."""
    if not state.turn.final_round and state.current_player.points >= TARGET_POINTS:
        state.turn.final_round = True
    round_complete = state.turn.active_player == len(state.players) - 1
    if state.turn.consecutive_passes >= 2 or (state.turn.final_round and round_complete):
        state.turn.finished = True
        scores = [(player.points, -player.card_count)
                  for player in state.players]
        best = max(scores)
        winners = [index for index, score in enumerate(scores) if score == best]
        state.turn.winner = winners[0] if len(winners) == 1 else None
    else:
        state.turn.active_player = (state.turn.active_player + 1) % len(state.players)
        if round_complete:
            state.turn.round_number += 1
