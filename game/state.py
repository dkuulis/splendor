from .constants import GOLD, TOKENS
from .player import Player
from .turn import Turn


def format_cost(cost):
    return ", ".join(f"{cost[token]} {token}" for token in TOKENS if cost.get(token, 0)) or "no gems"


class State:
    """Game state and legal turn transitions."""

    def __init__(self):
        self.players = [Player("YOU"), Player("COMPUTER", is_ai=True)]
        self.supply = {token: 5 if token == GOLD else 4 for token in TOKENS}
        # Pending token counts by type; unselected types are omitted.
        self.selected_tokens = {}
        self.selected_card = None
        # Every tier is always present; no cards means an empty list, not None.
        self.decks = {tier: [] for tier in (1, 2, 3)}
        self.market = {tier: [] for tier in (1, 2, 3)}
        self.nobles = []
        self.turn = Turn()
        self.log = []
        self.target_points = 15
        self.token_limit = 10

    @property
    def current_player(self):
        return self.players[self.turn.active_player]

    @property
    def max_take(self):
        return min(3, max(0, self.token_limit - sum(self.current_player.tokens.values())))

    def select_card(self, card):
        if not self.can_buy(card):
            return
        self.selected_tokens.clear()
        self.selected_card = None if self.selected_card is card else card

    def select_token(self, token):
        if (self.turn.finished or token not in TOKENS or token == GOLD
                or not self.supply.get(token, 0)):
            return
        self.selected_card = None
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
            return "Buy"
        return "Take" if self.selected_tokens else "Pass"

    @property
    def action_error(self):
        """Return why the selected action is illegal, or None when it is legal."""
        if self.selected_card is not None:
            return self.buy_card_error()
        if self.selected_tokens:
            return self.take_tokens_error()
        return "The game has already ended." if self.turn.finished else None

    def perform_action(self):
        """Validate and execute the selection, passing when nothing is selected."""
        if self.selected_card is not None:
            self.buy_card()
        elif self.selected_tokens:
            self.take_tokens()
        else:
            self.pass_turn()

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
        if (not 1 <= len(self.selected_tokens) <= 3
                or any(amount != 1 for amount in self.selected_tokens.values())):
            return "Select one to three different token types."
        if any(token not in TOKENS or token == GOLD or self.supply.get(token, 0) < 1
               for token in self.selected_tokens):
            return "A selected gem is not available."
        if len(self.selected_tokens) > self.max_take:
            return f"You cannot hold more than {self.token_limit} gems."
        return None

    def take_tokens(self):
        error = self.take_tokens_error()
        if error is not None:
            raise ValueError(error)
        for token in self.selected_tokens:
            self.supply[token] -= 1
            self.current_player.tokens[token] = self.current_player.tokens.get(token, 0) + 1

        taken = ", ".join(token for token in TOKENS if token in self.selected_tokens)
        self.log.append(f"{self.current_player.name} took {taken}.")
        self.turn.consecutive_passes = 0
        self.finish_turn()

    def card_cost(self, card):
        discounts = self.current_player.discounts
        return {token: max(0, amount - discounts.get(token, 0)) for token, amount in card.cost.items()}

    def can_buy(self, card):
        if self.turn.finished or card not in self.market.get(card.tier, []):
            return False
        return all(self.current_player.tokens.get(token, 0) >= amount
                   for token, amount in self.card_cost(card).items())

    def buy_card_error(self):
        """Return why a purchase is illegal, or None when it is legal."""
        if self.turn.finished:
            return "The game has already ended."
        if (self.selected_card is None
                or self.selected_card not in self.market.get(self.selected_card.tier, [])):
            return "That card is no longer in the market."
        if not self.can_buy(self.selected_card):
            return "You do not have enough gems/gold to buy that card."
        return None

    def buy_card(self):
        error = self.buy_card_error()
        if error is not None:
            raise ValueError(error)
        player = self.current_player
        card = self.selected_card
        cost = self.card_cost(card)
        for token, amount in cost.items():
            if amount:
                player.tokens[token] -= amount
                self.supply[token] = self.supply.get(token, 0) + amount
                if player.tokens[token] == 0:
                    del player.tokens[token]
        player.add_card(card)
        row = self.market[card.tier]
        slot = row.index(card)
        revealed = None
        if self.decks[card.tier]:
            revealed = self.decks[card.tier].pop(0)
            row[slot] = revealed
        else:
            row.pop(slot)
        payment = format_cost(cost)
        self.log.append(f"{card.points}-point {card.token} card (level {card.tier}) bought by {player.name} for {payment}.")
        if revealed is not None:
            revealed_cost = format_cost(revealed.cost)
            self.log.append(f"Revealed: {revealed.points}-point {revealed.token} card (level {revealed.tier}), costing {revealed_cost}.")
        self.turn.consecutive_passes = 0
        self.finish_turn()

    def assign_noble(self):
        """Award the first qualifying available noble, at most one per turn."""
        player = self.current_player
        discounts = player.discounts
        for noble in self.nobles:
            if all(discounts.get(token, 0) >= count
                   for token, count in noble.requirements.items()):
                self.nobles.remove(noble)
                player.nobles.append(noble)
                self.log.append(f"{player.name} received noble for {noble.points} points.")
                break

    def finish_turn(self):
        self.assign_noble()
        self.clear_selection()
        if not self.turn.final_round and self.current_player.points >= self.target_points:
            self.turn.final_round = True
            self.log.append(f"{self.current_player.name} reached {self.current_player.points} points "
                            "and triggered the final round.")
        round_complete = self.turn.active_player == len(self.players) - 1
        if self.turn.consecutive_passes >= 2 or (self.turn.final_round and round_complete):
            self.turn.finished = True
            scores = [(player.points, -sum(len(cards) for cards in player.cards.values()))
                      for player in self.players]
            best = max(scores)
            winners = [index for index, score in enumerate(scores) if score == best]
            self.turn.winner = winners[0] if len(winners) == 1 else None
            result = "Draw." if self.turn.winner is None else f"{self.players[self.turn.winner].name} wins."
            reason = "Two consecutive passes." if self.turn.consecutive_passes >= 2 else "Final round complete."
            self.log.append(f"Game over: {reason} {result}")
        else:
            self.turn.active_player = (self.turn.active_player + 1) % len(self.players)
            if round_complete:
                self.turn.round_number += 1

    def is_active_player(self, player):
        return not self.turn.finished and player is self.current_player
