from .constants import TOKENS


class Player:
    def __init__(self, name, is_ai=False):
        self.name = name
        self.is_ai = is_ai
        self.tokens = {}
        self.cards = {token: [] for token in TOKENS if token != "Gold"}
        self.nobles = []

    @property
    def points(self):
        return (sum(card.points for cards in self.cards.values() for card in cards)
                + sum(noble.points for noble in self.nobles))

    @property
    def discounts(self):
        return {token: len(cards) for token, cards in self.cards.items() if cards}
