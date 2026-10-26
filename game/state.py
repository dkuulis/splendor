from .constants import (GOLD, TOKENS, TOKEN_LIMIT, MAX_TAKE,
                        INITIAL_GOLD_SUPPLY, INITIAL_GEM_SUPPLY, MAX_RESERVATIONS)
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

    @property
    def action_error(self):
        """Return why the selected action is illegal, or None when it is legal."""
        kind = self.selection.action_kind
        if kind == "reserve":
            return self.reserve_card_error()
        if kind == "buy":
            return self.buy_card_error()
        if kind == "pass":
            return self.pass_turn_error()
        return self.take_tokens_error()

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

    def pass_turn_error(self):
        if self.turn.finished:
            return "The game has already ended."
        return None

    def pass_turn(self):
        error = self.pass_turn_error()
        if error is not None:
            raise ValueError(error)
        self.turn.consecutive_passes += 1
        self.finish_turn()

    def take_tokens_error(self):
        """Return why a gem collection is illegal, or None when it is legal."""
        if self.turn.finished:
            return "The game has already ended."
        if (len(self.selection.tokens) > MAX_TAKE
                or any(amount != 1 for amount in self.selection.tokens.values())):
            return "Select up to three different token types."
        if any(token not in TOKENS or token == GOLD or self.supply.get(token, 0) < 1
               for token in self.selection.tokens):
            return "A selected gem is not available."
        if len(self.selection.tokens) > self.current_player.max_take:
            return f"You cannot hold more than {TOKEN_LIMIT} gems."
        return None

    def take_tokens(self):
        error = self.take_tokens_error()
        if error is not None:
            raise ValueError(error)
        if not self.selection.tokens:
            self.pass_turn()
            return
        for token in self.selection.tokens:
            self.supply[token] -= 1
            self.current_player.tokens[token] = self.current_player.tokens.get(token, 0) + 1

        self.turn.consecutive_passes = 0
        self.finish_turn()

    @property
    def selected_card_affordable(self):
        return self.selection.card is not None and self.can_buy(self.selection.card)

    def can_buy(self, card):
        if self.turn.finished or not self.card_available(card):
            return False
        return all(self.current_player.tokens.get(token, 0) >= amount
                   for token, amount in self.current_player.card_payment(card).items())

    def card_available(self, card):
        return (card in self.market[card.tier]
                or card in self.current_player.reserved_cards)

    def buy_card_error(self):
        """Return why a purchase is illegal, or None when it is legal."""
        if self.turn.finished:
            return "The game has already ended."
        if self.selection.tokens.get(GOLD, 0):
            return "Deselect gold before buying a card."
        if self.selection.card is None or not self.card_available(self.selection.card):
            return "That card is not in the market or your reserved cards."
        if not self.can_buy(self.selection.card):
            return "You do not have enough gems/gold to buy that card."
        return None

    def buy_card(self):
        error = self.buy_card_error()
        if error is not None:
            raise ValueError(error)
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

    def reserve_card_error(self):
        """Return why a reservation is illegal, or None when it is legal."""
        if self.turn.finished:
            return "The game has already ended."
        if self.selection.card in self.current_player.reserved_cards:
            return "That card is already reserved."
        if (self.selection.card is None
                or self.selection.card not in self.market[self.selection.card.tier]):
            return "That card is no longer in the market."
        if self.selection.tokens != {GOLD: 1}:
            return "Select one gold token to reserve a card."
        if self.supply.get(GOLD, 0) < 1:
            return "Gold is not available."
        if len(self.current_player.reserved_cards) >= MAX_RESERVATIONS:
            return f"You cannot reserve more than {MAX_RESERVATIONS} cards."
        if self.current_player.token_count >= TOKEN_LIMIT:
            return f"You cannot hold more than {TOKEN_LIMIT} gems."
        return None

    def reserve_card(self):
        error = self.reserve_card_error()
        if error is not None:
            raise ValueError(error)
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
