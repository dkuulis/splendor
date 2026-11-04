"""Shared simulation evaluation and move selection."""

from game.constants import GOLD, MAX_TAKE, TOKENS
from simulation import Move, State as SimulationState, generate_moves
from simulation.constants import EMPTY_TOKENS, GEM_INDICES, GOLD_INDEX
from simulation.generate import completed_transfers, nobles_by_bonus

from .move_selection import update_selection_from_move


def evaluate(state, player_index):
    """Score a simulated position; larger tuples are better.

    Like GreedyAI, estimate collection turns before missing gem count.
    Points (including nobles) and permanent bonuses take precedence;
    remaining tokens break ties in favor of cheaper purchases.
    """
    player = state.players[player_index]
    targets = []
    visible = [index for row in state.market_indices for index in row]
    visible.extend(index for index, card in enumerate(state.cards)
                   if card.owner == player_index and not card.purchased)
    for index in visible:
        card = state.cards[index]
        missing = [max(0, card.cost[token] - player.discounts[token]
                       - player.tokens[token]) for token in GEM_INDICES]
        # Wildcards cover the largest shortages first to reduce turns.
        for _ in range(player.tokens[GOLD_INDEX]):
            largest = max(range(len(missing)), key=missing.__getitem__)
            if missing[largest] == 0:
                break
            missing[largest] -= 1
        total = sum(missing)
        if total and not any(amount and state.supply[token]
                             for token, amount in zip(GEM_INDICES, missing)):
            continue
        turns = max(max(missing), (total + MAX_TAKE - 1) // MAX_TAKE)
        targets.append((turns, total))
    turns, missing = min(targets, default=(float('inf'), float('inf')))
    return player.points, player.card_count, -turns, -missing, player.token_count


def make_selection(state, selection, score_move):
    """Score each simulated move and convert the best into pending choices."""
    selection.clear()
    position = SimulationState.from_game(state)
    player_index = state.turn.active_player
    cards = {index: card for row, tier in zip(position.market_indices, (1, 2, 3))
             for index, card in zip(row, state.market[tier])}
    reserved = [index for index, card in enumerate(position.cards)
                if card.owner == player_index and not card.purchased]
    cards.update(zip(reserved, state.current_player.reserved_cards))

    best_move = None
    best_score = None
    if selection.returning:
        noble = nobles_by_bonus(position.players[player_index], position.nobles)[GOLD_INDEX]
        moves = [Move("take", tokens=delta, noble_index=noble)
                 for delta in completed_transfers(position.players[player_index], EMPTY_TOKENS)]
    else:
        moves = generate_moves(position, player_index)
    for move in moves:
        # The desktop rules require available gold for a reservation.
        if move.kind == "reserve" and not state.supply.get(GOLD, 0):
            continue
        move.make(position, player_index)
        try:
            score = score_move(position, player_index)
        finally:
            move.unmake(position, player_index)
        if best_score is None or score > best_score:
            best_move, best_score = move, score

    if best_move is None:
        return

    if selection.returning:
        for token, amount in zip(TOKENS, best_move.tokens):
            for _ in range(-amount):
                selection.select_return_token(token, state)
    else:
        update_selection_from_move(best_move, state, cards, selection)
