from .constants import GEMS


class Player:
    def __init__(self, name, is_ai=False):
        self.name = name
        self.is_ai = is_ai
        self.tokens = {}
        self.cards = {token: [] for token in GEMS}
        self.reserved_cards = []
        self.nobles = []

    def add_card(self, card):
        self.cards[card.token].append(card)
        return card

    @property
    def points(self):
        return (sum(card.points for cards in self.cards.values() for card in cards)
                + sum(noble.points for noble in self.nobles))

    @property
    def discounts(self):
        return {token: len(cards) for token, cards in self.cards.items() if cards}
