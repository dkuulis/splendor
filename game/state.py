from .constants import GOLD, TOKENS, INITIAL_GOLD_SUPPLY, INITIAL_GEM_SUPPLY, TOKEN_LIMIT
from .player import Player
from .noble import assign_noble
from .turn import Turn, advance_turn


class State:
    """Game state and action execution; callers must supply allowed actions."""

    def __init__(self):
        self.players = [Player("YOU"), Player("COMPUTER", is_ai=True)]
        self.supply = {token: INITIAL_GOLD_SUPPLY if token == GOLD else INITIAL_GEM_SUPPLY
                       for token in TOKENS}
        # Every tier is always present; no cards means an empty list, not None.
        self.decks = {tier: [] for tier in (1, 2, 3)}
        self.market = {tier: [] for tier in (1, 2, 3)}
        self.nobles = []
        self.turn = Turn()

    @property
    def current_player(self):
        return self.players[self.turn.active_player]

    @property
    def return_required(self):
        return self.current_player.token_count > TOKEN_LIMIT

    def pass_turn(self):
        self.finish_turn(passed=True)

    def take_tokens(self, tokens):
        for token, amount in tokens.items():
            self.supply[token] -= amount
            self.current_player.tokens[token] = self.current_player.tokens.get(token, 0) + amount

        if not self.return_required:
            self.finish_turn(passed=False)

    def return_tokens(self, tokens):
        for token, amount in tokens.items():
            self.current_player.tokens[token] -= amount
            self.supply[token] += amount
            if not self.current_player.tokens[token]:
                del self.current_player.tokens[token]
        self.finish_turn(passed=False)

    def can_buy(self, card):
        if (card is None or self.turn.finished or self.return_required
                or not self.card_available(card)):
            return False
        return all(self.current_player.tokens.get(token, 0) >= amount
                   for token, amount in self.current_player.card_payment(card).items())

    def card_available(self, card):
        return (card in self.market[card.tier]
                or card in self.current_player.reserved_cards)

    def buy_card(self, card):
        player = self.current_player
        cost = player.card_payment(card)
        for token, amount in cost.items():
            player.tokens[token] -= amount
            self.supply[token] = self.supply.get(token, 0) + amount
            if player.tokens[token] == 0:
                del player.tokens[token]
        player.add_card(card)
        if card in player.reserved_cards:
            player.reserved_cards.remove(card)
        else:
            self.remove_market_card(card)
        self.finish_turn(passed=False)

    def reserve_card(self, card):
        player = self.current_player
        player.reserved_cards.append(card)
        self.supply[GOLD] -= 1
        player.tokens[GOLD] = player.tokens.get(GOLD, 0) + 1
        self.remove_market_card(card)
        if not self.return_required:
            self.finish_turn(passed=False)

    def remove_market_card(self, card):
        """Remove a purchased or reserved card and reveal its replacement."""
        row = self.market[card.tier]
        slot = row.index(card)
        if self.decks[card.tier]:
            row[slot] = self.decks[card.tier].pop(0)
        else:
            row.pop(slot)

    def finish_turn(self, passed):
        self.turn.consecutive_passes = self.turn.consecutive_passes + 1 if passed else 0
        assign_noble(self.current_player, self.nobles)
        advance_turn(self)

    def is_active_player(self, player):
        return not self.turn.finished and player is self.current_player
