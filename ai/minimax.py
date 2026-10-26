"""Two-ply minimax using shared simulation search functions."""

from simulation import generate_moves

from .simulation_search import evaluate, make_selection


def evaluate_position(state, player_index, next_player):
    """Compare both players, giving finished wins and losses precedence."""
    if state.finished(next_player):
        winner = state.winner(next_player)
        result = 0 if winner is None else 1 if winner == player_index else -1
        return result, 0, 0, 0, 0, 0
    own = evaluate(state, player_index)
    opponent = evaluate(state, 1 - player_index)
    # Equal infinite target distances cancel rather than producing NaN.
    return (0,) + tuple(0 if first == second else first - second
                        for first, second in zip(own, opponent))


def score_move(state, player_index):
    """Return the least favorable score over the opponent's legal replies."""
    opponent = 1 - player_index
    if state.finished(opponent):
        return evaluate_position(state, player_index, opponent)
    worst_score = None
    for reply in generate_moves(state, opponent):
        reply.make(state, opponent)
        try:
            score = evaluate_position(state, player_index, player_index)
        finally:
            reply.unmake(state, opponent)
        if worst_score is None or score < worst_score:
            worst_score = score
    if worst_score is None:
        # No generated reply means the opponent passes.
        return evaluate_position(state, player_index, player_index)
    return worst_score


class MinimaxAI:
    """Choose the best move against the opponent's best reply."""

    def make_selection(self, state, selection):
        make_selection(state, selection, score_move)
