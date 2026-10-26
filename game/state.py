from .constants import (GOLD, TOKENS, TOKEN_LIMIT, MAX_TAKE,
                        INITIAL_GOLD_SUPPLY, INITIAL_GEM_SUPPLY, MAX_RESERVATIONS)
from .player import Player
from .noble import assign_noble
from .turn import Turn, advance_turn


def format_cost(cost):
    return ", ".join(f"{cost[token]} {token}" for token in TOKENS if cost.get(token, 0)) or "no gems"


class State:
    """Game state and legal turn transitions."""

    def __init__(self):
        self.players = [Player("YOU"), Player("COMPUTER", is_ai=True)]
        self.supply = {token: INITIAL_GOLD_SUPPLY if token == GOLD else INITIAL_GEM_SUPPLY
                       for token in TOKENS}
        # Pending token counts by type; unselected types are omitted.
        self.selected_tokens = {}
        self.selected_card = None
        # Every tier is always present; no cards means an empty list, not None.
        self.decks = {tier: [] for tier in (1, 2, 3)}
        self.market = {tier: [] for tier in (1, 2, 3)}
        self.nobles = []
        self.turn = Turn()
        self.log = []

    @property
    def current_player(self):
        return self.players[self.turn.active_player]

    def select_card(self, card):
        if self.turn.finished or not self.card_available(card):
            return
        self.selected_tokens.clear()
        self.selected_card = None if self.selected_card is card else card

    def select_token(self, token):
        if (self.turn.finished or token not in TOKENS
                or not self.supply.get(token, 0)):
            return
        if token == GOLD:
            if self.selected_card in self.current_player.reserved_cards:
                return
            self.selected_tokens.clear()
        else:
            self.selected_card = None
            self.selected_tokens.pop(GOLD, None)
        self.selected_tokens[token] = 1

    def deselect_token(self, token):
        if not self.turn.finished:
            self.selected_tokens.pop(token, None)

    def clear_selection(self):
        self.selected_tokens.clear()
        self.selected_card = None

    @property
    def action_label(self):
        if self.selected_card is not None:
            return "Reserve" if self.selected_tokens.get(GOLD, 0) else "Buy"
        return "Take"

    @property
    def action_error(self):
        """Return why the selected action is illegal, or None when it is legal."""
        if self.selected_card is not None:
            if self.selected_tokens.get(GOLD, 0):
                return self.reserve_card_error()
            return self.buy_card_error()
        return self.take_tokens_error()

    def perform_action(self):
        """Validate and execute the selection, passing when nothing is selected."""
        if self.selected_card is not None:
            if self.selected_tokens.get(GOLD, 0):
                self.reserve_card()
            else:
                self.buy_card()
        else:
            self.take_tokens()

    def pass_turn(self):
        if self.turn.finished:
            raise ValueError("The game has already ended.")
        self.log.append(f"{self.current_player.name} passed.")
        self.turn.consecutive_passes += 1
        self.finish_turn()

    def take_tokens_error(self):
        """Return why a gem collection is illegal, or None when it is legal."""
        if self.turn.finished:
            return "The game has already ended."
        if (len(self.selected_tokens) > MAX_TAKE
                or any(amount != 1 for amount in self.selected_tokens.values())):
            return "Select up to three different token types."
        if any(token not in TOKENS or token == GOLD or self.supply.get(token, 0) < 1
               for token in self.selected_tokens):
            return "A selected gem is not available."
        if len(self.selected_tokens) > self.current_player.max_take:
            return f"You cannot hold more than {TOKEN_LIMIT} gems."
        return None

    def take_tokens(self):
        error = self.take_tokens_error()
        if error is not None:
            raise ValueError(error)
        if not self.selected_tokens:
            self.pass_turn()
            return
        for token in self.selected_tokens:
            self.supply[token] -= 1
            self.current_player.tokens[token] = self.current_player.tokens.get(token, 0) + 1

        taken = ", ".join(token for token in TOKENS if token in self.selected_tokens)
        self.log.append(f"{self.current_player.name} took {taken}.")
        self.turn.consecutive_passes = 0
        self.finish_turn()

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
        if self.selected_tokens.get(GOLD, 0):
            return "Deselect gold before buying a card."
        if self.selected_card is None or not self.card_available(self.selected_card):
            return "That card is not in the market or your reserved cards."
        if not self.can_buy(self.selected_card):
            return "You do not have enough gems/gold to buy that card."
        return None

    def buy_card(self):
        error = self.buy_card_error()
        if error is not None:
            raise ValueError(error)
        player = self.current_player
        card = self.selected_card
        cost = player.card_payment(card)
        for token, amount in cost.items():
            player.tokens[token] -= amount
            self.supply[token] = self.supply.get(token, 0) + amount
            if player.tokens[token] == 0:
                del player.tokens[token]
        player.add_card(card)
        payment = format_cost(cost)
        self.log.append(f"{card.points}-point {card.token} card (level {card.tier}) bought by {player.name} for {payment}.")
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
        if self.selected_card in self.current_player.reserved_cards:
            return "That card is already reserved."
        if (self.selected_card is None
                or self.selected_card not in self.market[self.selected_card.tier]):
            return "That card is no longer in the market."
        if self.selected_tokens != {GOLD: 1}:
            return "Select one gold token to reserve a card."
        if self.supply.get(GOLD, 0) < 1:
            return "Gold is not available."
        if len(self.current_player.reserved_cards) >= MAX_RESERVATIONS:
            return f"You cannot reserve more than {MAX_RESERVATIONS} cards."
        if sum(self.current_player.tokens.values()) >= TOKEN_LIMIT:
            return f"You cannot hold more than {TOKEN_LIMIT} gems."
        return None

    def reserve_card(self):
        error = self.reserve_card_error()
        if error is not None:
            raise ValueError(error)
        player = self.current_player
        card = self.selected_card
        player.reserved_cards.append(card)
        self.supply[GOLD] -= 1
        player.tokens[GOLD] = player.tokens.get(GOLD, 0) + 1
        self.log.append(f"{card.points}-point {card.token} card (level {card.tier}) reserved by {player.name}, taking 1 Gold.")
        self.remove_market_card(card)
        self.turn.consecutive_passes = 0
        self.finish_turn()

    def remove_market_card(self, card):
        """Remove a purchased or reserved card and reveal its replacement."""
        row = self.market[card.tier]
        slot = row.index(card)
        revealed = None
        if self.decks[card.tier]:
            revealed = self.decks[card.tier].pop(0)
            row[slot] = revealed
        else:
            row.pop(slot)
        if revealed is not None:
            revealed_cost = format_cost(revealed.cost)
            self.log.append(f"Revealed: {revealed.points}-point {revealed.token} card (level {revealed.tier}), costing {revealed_cost}.")

    def finish_turn(self):
        message = assign_noble(self.current_player, self.nobles)
        if message:
            self.log.append(message)
        self.clear_selection()
        advance_turn(self)

    def is_active_player(self, player):
        return not self.turn.finished and player is self.current_player
