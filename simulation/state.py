"""Compact simulation data. Token vectors use game.constants.TOKENS order.

Cards and nobles retain stable indices. Card tiers and market/deck metadata use 0–2;
costs and requirements are tuples, and players are indexed objects.
Definitions retain rule-relevant values only, without artwork identifiers.
"""

from .constants import GEM_INDICES, GOLD, GOLD_INDEX, TOKENS, TARGET_POINTS, TOKEN_COUNT


class Card:
    def __init__(self, tier, token, points, cost, owner=None, purchased=False):
        self.tier = tier  # Zero-based index into the market/deck metadata arrays.
        self.token = token  # Integer index into TOKENS.
        self.points = points
        self.cost = tuple(cost)
        self.owner = owner
        self.purchased = purchased  # An owned, unpurchased card is reserved.


class Noble:
    def __init__(self, points, requirements, owner=None):
        self.points = points
        self.requirements = tuple(requirements)
        self.owner = owner  # None while available, otherwise player index 0 or 1.


class Player:
    def __init__(self, player_index):
        self.index = player_index
        self.tokens = [0] * TOKEN_COUNT
        self.discounts = [0] * TOKEN_COUNT
        self.token_count = 0
        self.card_count = 0
        self.points = 0

    def payment(self, card):
        """Signed payment using matching gems first, or None if unaffordable."""
        tokens = self.tokens
        discounts = self.discounts
        available_gold = tokens[GOLD_INDEX]
        payment = [0] * TOKEN_COUNT
        gold = 0
        for token in GEM_INDICES:
            cost = max(0, card.cost[token] - discounts[token])
            matching = min(cost, tokens[token])
            payment[token] = -matching
            gold += cost - matching
            if gold > available_gold:
                return None
        payment[GOLD_INDEX] = -gold
        return tuple(payment)


class State:
    """Two-player search position, independent of the desktop game's models.

    players[player_index] owns token/discount arrays and incremental totals.
    Gold discount stays zero. Populate them consistently when building
    positions manually, or use from_game once at the simulation boundary.
    """

    def __init__(self):
        self.players = [Player(0), Player(1)]
        self.supply = [0] * TOKEN_COUNT
        self.cards = []
        self.market_indices = [[], [], []]
        # Unrevealed cards occupy [deck_starts[tier]:deck_ends[tier]]. Empty
        # draws advance deck_starts past the end so they can be undone.
        self.deck_starts = [0, 0, 0]
        self.deck_ends = [0, 0, 0]
        self.nobles = []

    @property
    def final_round(self):
        return any(player.points >= TARGET_POINTS for player in self.players)

    def finished(self, player_index):
        """Whether play has ended, given the player who would move next."""
        return player_index == 0 and self.final_round

    def winner(self, player_index):
        """Finished result: player index, or None for a draw/unfinished game."""
        if not self.finished(player_index):
            return None
        first = (self.players[0].points, -self.players[0].card_count)
        second = (self.players[1].points, -self.players[1].card_count)
        return None if first == second else 0 if first > second else 1

    @classmethod
    def from_game(cls, source):
        """Copy a duck-typed desktop position once; import no game models.

        Definitions and arrays are independent of source. Hidden deck order is
        copied for reproducibility; an AI must sample unknown order before search.
        Market slots and deck ranges reference the shared card array by index.
        Call at a turn boundary, after any required returns have completed.
        """
        state = cls()

        def convert_card(card, owner=None, purchased=False):
            return Card(card.tier - 1, TOKENS.index(card.token), card.points,
                        [card.cost.get(token, 0) for token in TOKENS], owner, purchased)

        def convert_noble(noble, owner=None):
            return Noble(noble.points,
                         [noble.requirements.get(token, 0) for token in TOKENS], owner)

        state.supply = [source.supply.get(token, 0) for token in TOKENS]
        for tier_index, tier in enumerate((1, 2, 3)):
            for card in source.market[tier]:
                state.market_indices[tier_index].append(len(state.cards))
                state.cards.append(convert_card(card))
            state.deck_starts[tier_index] = len(state.cards)
            state.cards.extend(convert_card(card) for card in source.decks[tier])
            state.deck_ends[tier_index] = len(state.cards)
        state.nobles = [convert_noble(noble) for noble in source.nobles]
        for player_index, player in enumerate(source.players):
            simulated_player = state.players[player_index]
            simulated_player.tokens = [player.tokens.get(token, 0) for token in TOKENS]
            simulated_player.discounts = [0 if token == GOLD else len(player.cards[token])
                                      for token in TOKENS]
            simulated_player.token_count = sum(simulated_player.tokens)
            simulated_player.card_count = player.card_count
            simulated_player.points = player.points
            for owned_cards in player.cards.values():
                state.cards.extend(convert_card(card, player_index, purchased=True) for card in owned_cards)
            state.cards.extend(convert_card(card, player_index) for card in player.reserved_cards)
            state.nobles.extend(convert_noble(noble, player_index) for noble in player.nobles)
        return state
