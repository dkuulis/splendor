from .constants import GOLD, TOKENS, INITIAL_GOLD_SUPPLY, INITIAL_GEM_SUPPLY
from .player import Player
from .selection import Selection
from .noble import assign_noble
from .turn import Turn, advance_turn


class State:
    """Game state and legal turn transitions."""

    def __init__(self):
        self.players = [Player("YOU"), Player("COMPUTER", is_ai=True)]
        self.supply = {token: INITIAL_GOLD_SUPPLY if token == GOLD else INITIAL_GEM_SUPPLY
                       for token in TOKENS}
        self.selection = Selection()
        # Every tier is always present; no cards means an empty list, not None.
        self.decks = {tier: [] for tier in (1, 2, 3)}
        self.market = {tier: [] for tier in (1, 2, 3)}
        self.nobles = []
        self.turn = Turn()

    @property
    def current_player(self):
        return self.players[self.turn.active_player]

    def perform_action(self):
        """Validate and execute the selection, passing when nothing is selected."""
        kind = self.selection.action_kind
        if kind == "reserve":
            self.reserve_card()
        elif kind == "buy":
            self.buy_card()
        elif kind == "pass":
            self.pass_turn()
        else:
            self.take_tokens()

    def pass_turn(self):
        if not self.selection.can_pass_turn(self):
            raise ValueError("Cannot pass after the game has ended.")
        self.turn.consecutive_passes += 1
        self.finish_turn()

    def take_tokens(self):
        if not self.selection.can_take_tokens(self):
            raise ValueError("Cannot take the selected tokens.")
        if not self.selection.tokens:
            self.pass_turn()
            return
        for token in self.selection.tokens:
            self.supply[token] -= 1
            self.current_player.tokens[token] = self.current_player.tokens.get(token, 0) + 1

        self.turn.consecutive_passes = 0
        self.finish_turn()

    def can_buy(self, card):
        if card is None or self.turn.finished or not self.card_available(card):
            return False
        return all(self.current_player.tokens.get(token, 0) >= amount
                   for token, amount in self.current_player.card_payment(card).items())

    def card_available(self, card):
        return (card in self.market[card.tier]
                or card in self.current_player.reserved_cards)

    def buy_card(self):
        if not self.selection.can_buy_card(self):
            raise ValueError("Cannot buy the selected card.")
        player = self.current_player
        card = self.selection.card
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
        self.turn.consecutive_passes = 0
        self.finish_turn()

    def reserve_card(self):
        if not self.selection.can_reserve_card(self):
            raise ValueError("Cannot reserve the selected card.")
        player = self.current_player
        card = self.selection.card
        player.reserved_cards.append(card)
        self.supply[GOLD] -= 1
        player.tokens[GOLD] = player.tokens.get(GOLD, 0) + 1
        self.remove_market_card(card)
        self.turn.consecutive_passes = 0
        self.finish_turn()

    def remove_market_card(self, card):
        """Remove a purchased or reserved card and reveal its replacement."""
        row = self.market[card.tier]
        slot = row.index(card)
        if self.decks[card.tier]:
            row[slot] = self.decks[card.tier].pop(0)
        else:
            row.pop(slot)

    def finish_turn(self):
        assign_noble(self.current_player, self.nobles)
        self.selection.clear()
        advance_turn(self)

    def is_active_player(self, player):
        return not self.turn.finished and player is self.current_player
