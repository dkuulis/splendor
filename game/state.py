from .constants import COLORS
from .player import Player
from .turn import Turn


def format_cost(cost):
    return ", ".join(f"{cost[color]} {color}" for color in COLORS if cost.get(color, 0)) or "no gems"


class State:
    """Game state and legal turn transitions."""

    def __init__(self):
        self.players = [Player("YOU"), Player("COMPUTER", is_ai=True)]
        self.bank = dict.fromkeys(COLORS, 4)
        # Every tier is always present; no cards means an empty list, not None.
        self.decks = {tier: [] for tier in (1, 2, 3)}
        self.market = {tier: [] for tier in (1, 2, 3)}
        self.turn = Turn()
        self.log = []
        self.target_points = 15
        self.gem_limit = 10

    @property
    def current_player(self):
        return self.players[self.turn.active_player]

    @property
    def max_take(self):
        return min(3, max(0, self.gem_limit - sum(self.current_player.gems.values())))

    def pass_turn(self):
        if self.turn.finished:
            raise ValueError("The game has already ended.")
        self.log.append(f"{self.current_player.name} passed.")
        self.turn.consecutive_passes += 1
        self.finish_turn()

    def take_gems(self, colors):
        if self.turn.finished:
            raise ValueError("The game has already ended.")
        colors = list(colors)
        if not 1 <= len(colors) <= 3 or len(set(colors)) != len(colors):
            raise ValueError("Select one to three different gem colors.")
        if any(color not in COLORS or self.bank.get(color, 0) < 1 for color in colors):
            raise ValueError("A selected gem is not available.")
        player = self.current_player
        if len(colors) > self.max_take:
            raise ValueError(f"You cannot hold more than {self.gem_limit} gems.")
        for color in colors:
            self.bank[color] -= 1
            player.gems[color] = player.gems.get(color, 0) + 1
        gems = ", ".join(color for color in COLORS if color in colors)
        self.log.append(f"{player.name} took {gems}.")
        self.turn.consecutive_passes = 0
        self.finish_turn()

    def card_cost(self, card):
        discounts = self.current_player.discounts
        return {color: max(0, amount - discounts.get(color, 0)) for color, amount in card.cost.items()}

    def can_buy(self, card):
        if self.turn.finished or card not in self.market.get(card.tier, []):
            return False
        player = self.current_player
        return all(player.gems.get(color, 0) >= amount for color, amount in self.card_cost(card).items())

    def buy_card(self, card):
        if self.turn.finished:
            raise ValueError("The game has already ended.")
        if card not in self.market.get(card.tier, []):
            raise ValueError("That card is no longer in the market.")
        if not self.can_buy(card):
            raise ValueError("You do not have enough gems to buy that card.")
        player = self.current_player
        cost = self.card_cost(card)
        for color, amount in cost.items():
            if amount:
                player.gems[color] -= amount
                self.bank[color] = self.bank.get(color, 0) + amount
                if player.gems[color] == 0:
                    del player.gems[color]
        player.cards[card.id] = card
        row = self.market[card.tier]
        slot = row.index(card)
        revealed = None
        if self.decks[card.tier]:
            revealed = self.decks[card.tier].pop(0)
            row[slot] = revealed
        else:
            row.pop(slot)
        payment = format_cost(cost)
        self.log.append(f"{card.points}-point {card.color} card (level {card.tier}) bought by {player.name} for {payment}.")
        if revealed is not None:
            revealed_cost = format_cost(revealed.cost)
            self.log.append(f"Revealed: {revealed.points}-point {revealed.color} card (level {revealed.tier}), costing {revealed_cost}.")
        self.turn.consecutive_passes = 0
        self.finish_turn()

    def finish_turn(self):
        if not self.turn.final_round and self.current_player.points >= self.target_points:
            self.turn.final_round = True
            player = self.current_player
            self.log.append(f"{player.name} reached {player.points} points and triggered the final round.")
        round_complete = self.turn.active_player == len(self.players) - 1
        if self.turn.consecutive_passes >= 2 or (self.turn.final_round and round_complete):
            self.turn.finished = True
            scores = [(player.points, -len(player.cards)) for player in self.players]
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

    def player_status(self, player):
        """Return a player's game status without UI-specific wording."""
        player_index = self.players.index(player)
        if self.turn.finished:
            if self.turn.winner is None:
                return "draw"
            return "winner" if self.turn.winner == player_index else "lost"
        return "active" if self.turn.active_player == player_index else "waiting"
