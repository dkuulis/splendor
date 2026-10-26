from game.constants import COLORS


class GreedyAI:
    """Buy for points, otherwise collect scarce gems toward the closest card."""

    def play_turn(self, state):
        cards = [card for row in state.market.values() for card in row]
        affordable = [card for card in cards if state.can_buy(card)]
        if affordable:
            card = min(affordable, key=lambda card: (-card.points, sum(state.card_cost(card).values())))
            state.buy_card(card)
            return

        player = state.current_player
        capacity = min(3, state.gem_limit - sum(player.gems.values()))
        if capacity > 0:
            targets = []
            for card in cards:
                cost = state.card_cost(card)
                missing = {color: max(0, cost.get(color, 0) - player.gems.get(color, 0))
                           for color in COLORS}
                available = [color for color in COLORS if missing[color] and state.bank.get(color, 0)]
                if available:
                    targets.append((sum(missing.values()), available))
            if targets:
                # Stable ordering keeps ties in market / canonical gem order.
                _, colors = min(targets, key=lambda target: target[0])
                colors.sort(key=lambda color: state.bank[color])
                state.take_gems(colors[:capacity])
                return

        state.pass_turn()
