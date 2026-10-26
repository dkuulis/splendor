from .constants import GEMS, GOLD, TOKENS, MAX_TAKE, MAX_RESERVATIONS, TOKEN_LIMIT


class Selection:
    """Pending choices and the action they belong to."""

    def __init__(self):
        self.card = None
        # Pending token counts by type; unselected types are omitted.
        self.tokens = {}
        self.returning = False

    @property
    def action_kind(self):
        if self.returning:
            return "return"
        if GOLD in self.tokens:
            return "reserve"
        if self.card is not None:
            return "buy"
        if self.tokens:
            return "take"
        return "pass"

    def can_select_card(self, card, state):
        if (state.turn.finished or state.return_required or card is None
                or not state.card_available(card)):
            return False
        # README rules 3 and 7: reserved cards must be affordable to select;
        # an already selected card can still be deselected.
        return (self.card is card or card not in state.current_player.reserved_cards
                or state.can_buy(card))

    def can_select_token(self, token, state):
        if (state.turn.finished or state.return_required or token not in TOKENS
                or state.supply.get(token, 0) < 1
                or self.tokens.get(token, 0) >= state.supply[token]):
            return False
        # README rule 4: manual gold selection requires an affordable market card.
        return (token != GOLD or (self.card is not None
                and self.card in state.market[self.card.tier]
                and state.can_buy(self.card)))

    def can_deselect_token(self, token, state):
        # README rules 5–6: only selected tokens can be removed, and an
        # unaffordable market card must retain its gold.
        return (not state.turn.finished and token in self.tokens
                and (self.returning or token != GOLD or state.can_buy(self.card)))

    def can_select_return_token(self, token, state):
        return (not state.turn.finished and self.returning and state.return_required
                and token in TOKENS
                and self.tokens.get(token, 0) < state.current_player.tokens.get(token, 0))

    def select_return_token(self, token, state):
        if self.can_select_return_token(token, state):
            self.tokens[token] = self.tokens.get(token, 0) + 1

    def can_return_tokens(self, state):
        return (not state.turn.finished and self.returning and state.return_required
                and self.card is None
                and sum(self.tokens.values()) == state.current_player.token_count - TOKEN_LIMIT
                and all(token in TOKENS and amount > 0
                        and amount <= state.current_player.tokens.get(token, 0)
                        for token, amount in self.tokens.items()))

    def can_pass_turn(self, state):
        return not state.turn.finished and not state.return_required

    def can_take_tokens(self, state):
        count = sum(self.tokens.values())
        if (state.turn.finished or state.return_required
                or self.card is not None or not self.tokens
                or not all(token in TOKENS and token != GOLD and amount > 0
                           and state.supply.get(token, 0) >= amount
                           for token, amount in self.tokens.items())):
            return False
        distinct_count = min(MAX_TAKE, sum(state.supply.get(token, 0) > 0 for token in GEMS))
        return (count == distinct_count
                and all(amount == 1 for amount in self.tokens.values())
                or len(self.tokens) == 1 and count == 2
                and state.supply[next(iter(self.tokens))] >= 4)

    def can_buy_card(self, state):
        return not self.tokens and state.can_buy(self.card)

    def can_reserve_card(self, state):
        return (not state.turn.finished and not state.return_required and self.card is not None
                and self.card in state.market[self.card.tier]
                and self.card not in state.current_player.reserved_cards
                and self.tokens == {GOLD: 1} and state.supply.get(GOLD, 0) >= 1
                and len(state.current_player.reserved_cards) < MAX_RESERVATIONS)

    def can_perform_action(self, state):
        kind = self.action_kind
        if kind == "return":
            return self.can_return_tokens(state)
        if kind == "reserve":
            return self.can_reserve_card(state)
        if kind == "buy":
            return self.can_buy_card(state)
        if kind == "take":
            return self.can_take_tokens(state)
        return self.can_pass_turn(state)

    def perform_action(self, state):
        """Dispatch an allowed action; callers check can_perform_action first."""
        kind = self.action_kind
        if kind == "return":
            state.return_tokens(self.tokens)
        elif kind == "reserve":
            state.reserve_card(self.card)
        elif kind == "buy":
            state.buy_card(self.card)
        elif kind == "pass":
            state.pass_turn()
        else:
            state.take_tokens(self.tokens)
        self.clear()
        self.returning = state.return_required

    def select_card(self, card, state):
        if not self.can_select_card(card, state):
            return
        # README rule 7: clicking the selected card clears card and tokens.
        if self.card is card:
            self.clear()
            return
        affordable = state.can_buy(card)
        # README rules 2–3: replace the card and clear all selected tokens.
        self.clear()
        self.card = card
        # README rule 2: an unaffordable market card automatically selects gold.
        if not affordable:
            self.tokens[GOLD] = 1

    def select_token(self, token, state):
        if not self.can_select_token(token, state):
            return
        if token != GOLD:
            # README rule 1: clear card/gold, keeping other selected gem colors.
            self.card = None
            self.tokens.pop(GOLD, None)
        self.tokens[token] = self.tokens.get(token, 0) + 1

    def deselect_token(self, token, state):
        if not self.can_deselect_token(token, state):
            return
        # Remove one token at a time, preserving the other choices.
        self.tokens[token] -= 1
        if not self.tokens[token]:
            self.tokens.pop(token)

    def clear(self):
        """Clear pending choices without leaving the required return phase."""
        self.tokens.clear()
        self.card = None
