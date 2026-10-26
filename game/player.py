class Player:
    def __init__(self, name, is_ai=False):
        self.name = name
        self.is_ai = is_ai
        self.tokens = {}
        self.cards = {}
        self.nobles = []

    @property
    def points(self):
        return (sum(card.points for card in self.cards.values())
                + sum(noble.points for noble in self.nobles))

    @property
    def discounts(self):
        discounts = {}
        for card in self.cards.values():
            discounts[card.token] = discounts.get(card.token, 0) + 1
        return discounts
