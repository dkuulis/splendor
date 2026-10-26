from .constants import GOLD, TOKENS


class Selection:
    """Pending choices and the action they belong to."""

    def __init__(self):
        self.card = None
        # Pending token counts by type; unselected types are omitted.
        self.tokens = {}
        self.action_kind = "pass"

    def select_card(self, card, state):
        if state.turn.finished or not state.card_available(card):
            return
        if self.action_kind == "buy" and self.card is card:
            self.clear()
        elif (card not in state.current_player.reserved_cards
              and not state.can_buy(card)):
            self.reserve_card(card, state)
        else:
            self.clear()
            self.card = card
            self.action_kind = "buy"

    def reserve_card(self, card, state):
        if (state.turn.finished
                or (card is not None and card not in state.market[card.tier])):
            return
        if self.action_kind == "reserve" and card is not None and self.card is card:
            self.clear()
        else:
            self.clear()
            self.card = card
            self.tokens[GOLD] = 1
            self.action_kind = "reserve"

    def select_token(self, token, state):
        if (state.turn.finished or token not in TOKENS
                or not state.supply.get(token, 0)
                or (token == GOLD and self.action_kind == "buy"
                    and self.card in state.current_player.reserved_cards)):
            return
        if token == GOLD:
            if self.action_kind != "reserve":
                card = self.card if self.action_kind == "buy" else None
                self.reserve_card(card, state)
        else:
            if self.action_kind != "take":
                self.clear()
                self.action_kind = "take"
            self.tokens[token] = 1

    def deselect_token(self, token, state):
        if state.turn.finished:
            return
        if self.action_kind == "reserve" and token == GOLD:
            self.tokens.pop(GOLD, None)
            if self.card is None:
                self.clear()
            else:
                self.action_kind = "buy"
        elif self.action_kind == "take":
            self.tokens.pop(token, None)
            if not self.tokens:
                self.clear()

    def clear(self):
        self.tokens.clear()
        self.card = None
        self.action_kind = "pass"
