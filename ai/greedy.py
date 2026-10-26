from game.constants import TOKENS, MAX_TAKE


class GreedyAI:
    """Select cards for points, otherwise gems toward the quickest cards."""

    def make_selection(self, state, selection):
        selection.clear()
        cards = ([card for row in state.market.values() for card in row]
                 + state.current_player.reserved_cards)
        if self.select_card(state, selection, cards):
            return
        self.select_tokens(state, selection, cards)

    def select_card(self, state, selection, cards):
        """Select the best affordable card and report whether one was found."""
        affordable = [card for card in cards if state.can_buy(card)]
        if affordable:
            card = min(affordable, key=lambda card: (-card.points, sum(state.current_player.card_cost(card).values())))
            selection.select_card(card, state)
            return True
        return False

    def select_tokens(self, state, selection, cards):
        """Select useful gems toward visible cards."""
        capacity = state.current_player.max_take
        if capacity == 0:
            return

        tokens = []
        for _, _, available in self.rank_targets(state, cards):
            available.sort(key=lambda token: state.supply[token])
            for token in available:
                if token not in tokens and len(tokens) < capacity:
                    tokens.append(token)
            if len(tokens) == capacity:
                break
        for token in tokens:
            selection.select_token(token, state)

    def rank_targets(self, state, cards):
        """Rank collectible targets by turns needed, then missing gem count."""
        targets = []
        for card in cards:
            cost = state.current_player.card_cost(card)
            missing = {token: max(0, cost.get(token, 0) - state.current_player.tokens.get(token, 0))
                       for token in TOKENS}
            available = [token for token in TOKENS if missing[token] and state.supply.get(token, 0)]
            if available:
                total = sum(missing.values())
                # At most three tokens per turn, and only one of each type.
                turns = max(max(missing.values()), (total + MAX_TAKE - 1) // MAX_TAKE)
                targets.append((turns, total, available))
        # Prefer fewer gems when turn counts tie; otherwise keep market order.
        return sorted(targets, key=lambda target: target[:2])
