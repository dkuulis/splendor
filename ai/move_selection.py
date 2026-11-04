"""Translate simulation moves into pending desktop choices."""

from game.constants import GEMS, GOLD, MAX_TAKE, TOKENS, TOKEN_LIMIT
from simulation.generate import DISTINCT_TAKES, PAIR_TAKES


def update_selection_from_move(move, state, cards, selection):
    """Select the initial action of a complete simulated turn.

    cards maps simulation card indices to their desktop Card objects.
    Reserve requires gold in the desktop game. For a net take/return transfer,
    recover a legal take; the AI chooses returns on its next selection call.
    No game action is executed.
    """
    selection.clear()
    if move.card_index is not None:
        selection.select_card(cards[move.card_index], state)
        if move.kind == 'reserve' and GOLD not in selection.tokens:
            selection.select_token(GOLD, state)
    else:
        available = min(MAX_TAKE, sum(state.supply.get(token, 0) > 0 for token in GEMS))
        patterns = list(DISTINCT_TAKES.get(available, ()))
        patterns.extend(pattern for token, pattern in PAIR_TAKES
                        if state.supply.get(TOKENS[token], 0) >= 4)
        for taken in patterns:
            if (all(amount <= state.supply.get(token, 0) for token, amount in zip(TOKENS, taken))
                    and sum(taken) - sum(move.tokens) == max(
                        0, state.current_player.token_count + sum(taken) - TOKEN_LIMIT)
                    and all(0 <= amount - net <= state.current_player.tokens.get(token, 0) + amount
                            for token, amount, net in zip(TOKENS, taken, move.tokens))):
                break
        else:
            raise ValueError("Simulated transfer has no legal desktop take")
        for token, amount in zip(TOKENS, taken):
            for _ in range(amount):
                selection.select_token(token, state)
