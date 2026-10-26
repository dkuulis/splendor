"""Legal move enumeration using fixed token arrays and precomputed patterns."""

from itertools import combinations, combinations_with_replacement

from .constants import (
    EMPTY_TOKENS, GEM_INDICES, GOLD_INDEX, MAX_RESERVATIONS, MAX_TAKE, SINGLE_GOLD,
    TOKEN_COUNT, TOKEN_LIMIT,
)
from .move import Move


def token_vector(tokens):
    counts = [0] * TOKEN_COUNT
    for token in tokens:
        counts[token] += 1
    return tuple(counts)


DISTINCT_TAKES = {
    size: tuple(token_vector(colors) for colors in combinations(GEM_INDICES, size))
    for size in range(1, MAX_TAKE + 1)
}
PAIR_TAKES = tuple((token, token_vector((token, token))) for token in GEM_INDICES)
RETURN_PATTERNS = {
    excess: tuple(token_vector(tokens) for tokens in
                  combinations_with_replacement(range(TOKEN_COUNT), excess))
    for excess in range(1, MAX_TAKE + 1)
}


def nobles_by_bonus(player, nobles):
    """First unowned noble index per bonus; Gold means no added bonus."""
    discounts = player.discounts
    awards = [None] * TOKEN_COUNT
    for bonus in (GOLD_INDEX,) + GEM_INDICES:
        for index, noble in enumerate(nobles):
            if noble.owner is None and all(
                    discounts[token] + (token == bonus) >= noble.requirements[token]
                    for token in GEM_INDICES):
                awards[bonus] = index
                break
    return awards


def completed_transfers(player, taken):
    """Net deltas for a legal collection followed by every required return."""
    excess = player.token_count + sum(taken) - TOKEN_LIMIT
    if excess <= 0:
        yield taken
        return
    holdings = tuple(owned + amount for owned, amount in zip(player.tokens, taken))
    for returned in RETURN_PATTERNS[excess]:
        if all(owned >= amount for owned, amount in zip(holdings, returned)):
            yield tuple(amount - back for amount, back in zip(taken, returned))


def generate_moves(state, player_index):
    """Generate complete turns with signed net token transfers.

    Start at a turn boundary with at most ten tokens per player. Required
    returns are included in Take/Reserve; there is no separate Return phase.
    """
    player = state.players[player_index]

    reserved_indices = [index for index, card in enumerate(state.cards)
                        if card.owner == player_index and not card.purchased]

    nobles = nobles_by_bonus(player, state.nobles)
    # Several nobles can qualify after a purchase. Preserve the rule awarding
    # the first remaining qualifier on a later turn, even without a purchase.
    existing_noble = nobles[GOLD_INDEX]

    moves = []
    for row in state.market_indices:
        for card_index in row:
            card = state.cards[card_index]
            payment = player.payment(card)
            if payment is not None:
                moves.append(Move("buy", card_index=card_index, tokens=payment,
                                  noble_index=nobles[card.token]))
                
    for card_index in reserved_indices:
        card = state.cards[card_index]
        payment = player.payment(card)
        if payment is not None:
            moves.append(Move("buy_reserved", card_index=card_index, tokens=payment,
                              noble_index=nobles[card.token]))

    if len(reserved_indices) < MAX_RESERVATIONS:
        gold = SINGLE_GOLD if state.supply[GOLD_INDEX] > 0 else EMPTY_TOKENS
        transfers = tuple(completed_transfers(player, gold))
        moves.extend(Move("reserve", card_index=card_index, tokens=delta, noble_index=existing_noble)
                     for row in state.market_indices for card_index in row for delta in transfers)

    distinct_count = min(MAX_TAKE, sum(state.supply[token] > 0 for token in GEM_INDICES))
    patterns = [pattern for pattern in DISTINCT_TAKES.get(distinct_count, ())
                if all(available >= amount for available, amount in zip(state.supply, pattern))]
    patterns.extend(pattern for token, pattern in PAIR_TAKES if state.supply[token] >= 4)
    # Different take/return sequences can lead to the same net position.
    seen = {delta for pattern in patterns for delta in completed_transfers(player, pattern)}
    moves.extend(Move("take", tokens=delta, noble_index=existing_noble) for delta in seen)

    return moves
