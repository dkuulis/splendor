from game.constants import COLORS


class GreedyAI:
    """Buy for points, otherwise collect gems toward the quickest cards."""

    def play_turn(self, state):
        cards = [card for row in state.market.values() for card in row]
        if self.buy_card(state, cards):
            return
        if self.take_gems(state, cards):
            return
        state.pass_turn()

    def buy_card(self, state, cards):
        """Buy the best affordable card and report whether an action was taken."""
        affordable = [card for card in cards if state.can_buy(card)]
        if affordable:
            card = min(affordable, key=lambda card: (-card.points, sum(state.card_cost(card).values())))
            state.buy_card(card)
            return True
        return False

    def take_gems(self, state, cards):
        """Collect useful gems and report whether an action was taken."""
        capacity = state.max_take
        if capacity == 0:
            return False

        colors = []
        for _, _, available in self.rank_targets(state, cards):
            available.sort(key=lambda color: state.bank[color])
            for color in available:
                if color not in colors and len(colors) < capacity:
                    colors.append(color)
            if len(colors) == capacity:
                break
        if not colors:
            return False
        state.take_gems(colors)
        return True

    def rank_targets(self, state, cards):
        """Rank collectible targets by turns needed, then missing gem count."""
        player = state.current_player
        targets = []
        for card in cards:
            cost = state.card_cost(card)
            missing = {color: max(0, cost.get(color, 0) - player.gems.get(color, 0))
                       for color in COLORS}
            available = [color for color in COLORS if missing[color] and state.bank.get(color, 0)]
            if available:
                total = sum(missing.values())
                # At most three gems per turn, and only one of each color.
                turns = max(max(missing.values()), (total + 2) // 3)
                targets.append((turns, total, available))
        # Prefer fewer gems when turn counts tie; otherwise keep market order.
        return sorted(targets, key=lambda target: target[:2])
