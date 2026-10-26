from game.constants import TOKENS, MAX_TAKE

from .greedy import GreedyAI


class Greedy2AI(GreedyAI):
    """Include noble awards and progress when choosing cards and gem targets."""

    def noble_points(self, state, card):
        discounts = state.current_player.discounts
        discounts[card.token] += 1
        for noble in state.nobles:
            if all(discounts[token] >= count for token, count in noble.requirements.items()):
                return noble.points
        return 0

    def noble_distance(self, state, card):
        """Fewest missing bonuses for a noble this card advances, or infinity."""
        discounts = state.current_player.discounts
        distance = float('inf')
        for noble in state.nobles:
            if noble.requirements.get(card.token, 0) > discounts[card.token]:
                missing = sum(max(0, count - discounts[token])
                              for token, count in noble.requirements.items())
                distance = min(distance, missing)
        return distance

    def select_card(self, state, selection, cards):
        affordable = [card for card in cards if state.can_buy(card)]
        if affordable:
            card = min(affordable, key=lambda card: (
                -(card.points + self.noble_points(state, card)),
                self.noble_distance(state, card),
                sum(state.current_player.card_cost(card).values()),
            ))
            selection.select_card(card, state)
            return True
        return False

    def rank_targets(self, state, cards):
        """Rank by collection turns, noble progress, then missing gems."""
        targets = []
        for card in cards:
            cost = state.current_player.card_cost(card)
            missing = {token: max(0, cost.get(token, 0) - state.current_player.tokens.get(token, 0))
                       for token in TOKENS}
            available = [token for token in TOKENS if missing[token] and state.supply.get(token, 0)]
            if available:
                total = sum(missing.values())
                turns = max(max(missing.values()), (total + MAX_TAKE - 1) // MAX_TAKE)
                targets.append((turns, self.noble_distance(state, card), total, available))
        targets.sort(key=lambda target: target[:3])
        return [(turns, total, available) for turns, _, total, available in targets]
