"""Translate simulation moves into pending desktop choices."""

from game.constants import GOLD, TOKENS


def update_selection_from_move(move, state, cards, selection):
    """Replace pending choices with a move without returns, using original cards.

    cards maps simulation card indices to their desktop Card objects. Callers
    supply a move supported by desktop selection, including gold for Reserve.
    No game action is executed.
    """
    selection.clear()
    if move.card_index is not None:
        selection.select_card(cards[move.card_index], state)
        if move.kind == 'reserve' and GOLD not in selection.tokens:
            selection.select_token(GOLD, state)
    else:
        for token, amount in zip(TOKENS, move.tokens):
            for _ in range(amount):
                selection.select_token(token, state)
