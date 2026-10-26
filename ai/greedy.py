from game.constants import TOKENS


class GreedyAI:
    """Buy for points, otherwise collect gems toward the quickest cards."""

    def play_turn(self, state):
        cards = [card for row in state.market.values() for card in row]
        if self.buy_card(state, cards):
            return
        if self.take_tokens(state, cards):
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

    def take_tokens(self, state, cards):
        """Collect useful gems and report whether an action was taken."""
        capacity = state.max_take
        if capacity == 0:
            return False

        tokens = []
        for _, _, available in self.rank_targets(state, cards):
            available.sort(key=lambda token: state.supply[token])
            for token in available:
                if token not in tokens and len(tokens) < capacity:
                    tokens.append(token)
            if len(tokens) == capacity:
                break
        if not tokens:
            return False
        state.take_tokens(tokens)
        return True

    def rank_targets(self, state, cards):
        """Rank collectible targets by turns needed, then missing gem count."""
        player = state.current_player
        targets = []
        for card in cards:
            cost = state.card_cost(card)
            missing = {token: max(0, cost.get(token, 0) - player.tokens.get(token, 0))
                       for token in TOKENS}
            available = [token for token in TOKENS if missing[token] and state.supply.get(token, 0)]
            if available:
                total = sum(missing.values())
                # At most three tokens per turn, and only one of each type.
                turns = max(max(missing.values()), (total + 2) // 3)
                targets.append((turns, total, available))
        # Prefer fewer gems when turn counts tie; otherwise keep market order.
        return sorted(targets, key=lambda target: target[:2])
