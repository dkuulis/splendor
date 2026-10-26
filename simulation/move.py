"""Reversible execution on simulation.State, with no desktop model dependency."""

from .constants import EMPTY_TOKENS


class Move:
    """Complete reversible action; tokens are signed net transfers.

    Positive counts enter the player's holdings; negative counts return to the
    supply. Reserve includes gold and any returns; Buy contains the actual
    discounted gem/gold payment as negative counts, calculated at generation.
    """

    def __init__(self, kind, card_index=None, tokens=EMPTY_TOKENS, noble_index=None):
        # Action to execute: "buy", "buy_reserved", "reserve", or "take".
        self.kind = kind
        # Stable index into state.cards; None for token takes.
        self.card_index = card_index
        # Net transfer in TOKENS order: positive gains, negative payments or
        # returns. Includes reservation gold and any required returns.
        self.tokens = tuple(tokens)
        # Stable index into state.nobles to award; None when no noble qualifies.
        # Make assigns its owner; unmake clears ownership and reverses points.
        self.noble_index = noble_index

    def make(self, state, player_index):
        """Apply this effect for player_index without modifying the move.

        Unwind nested moves in reverse order using the same player indices.
        """
        player = state.players[player_index]
        card = state.cards[self.card_index] if self.card_index is not None else None

        # Accounting.
        if self.kind in ("buy", "buy_reserved"):
            player.discounts[card.token] += 1
            player.card_count += 1
            player.points += card.points

        if card is not None:
            # Cards.
            if self.kind in ("buy", "reserve"):
                tier_index = card.tier
                row = state.market_indices[tier_index]
                row.remove(self.card_index)
                replacement_index = state.deck_starts[tier_index]
                # Advance even for empty draws: positions past deck_ends are
                # virtual sentinels, so undo needs no refill flag.
                state.deck_starts[tier_index] += 1
                if replacement_index < state.deck_ends[tier_index]:
                    row.append(replacement_index)

            card.owner = player_index
            card.purchased = self.kind in ("buy", "buy_reserved")

        # Tokens.
        for token, amount in enumerate(self.tokens):
            player.tokens[token] += amount
            state.supply[token] -= amount
        player.token_count += sum(self.tokens)

        # Nobles.
        if self.noble_index is not None:
            noble = state.nobles[self.noble_index]
            noble.owner = player_index
            player.points += noble.points

    def unmake(self, state, player_index):
        """Reverse this effect in place without modifying the move."""
        player = state.players[player_index]
        card = state.cards[self.card_index] if self.card_index is not None else None

        # Accounting.
        if self.kind in ("buy", "buy_reserved"):
            player.discounts[card.token] -= 1
            player.card_count -= 1
            player.points -= card.points

        if card is not None:
            # Cards.
            card.purchased = False
            if self.kind in ("buy", "reserve"):
                card.owner = None
                tier_index = card.tier
                row = state.market_indices[tier_index]
                state.deck_starts[tier_index] -= 1
                replacement_index = state.deck_starts[tier_index]
                if replacement_index < state.deck_ends[tier_index]:
                    row.remove(replacement_index)
                row.append(self.card_index)

        # Tokens.
        for token, amount in enumerate(self.tokens):
            player.tokens[token] -= amount
            state.supply[token] += amount
        player.token_count -= sum(self.tokens)

        # Nobles.
        if self.noble_index is not None:
            noble = state.nobles[self.noble_index]
            noble.owner = None
            player.points -= noble.points
