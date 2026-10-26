from .constants import GEMS, GOLD, MAX_TAKE, TOKEN_LIMIT


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
    def token_count(self):
        return sum(self.tokens.values())

    @property
    def card_count(self):
        return sum(len(cards) for cards in self.cards.values())

    @property
    def max_take(self):
        return min(MAX_TAKE, max(0, TOKEN_LIMIT - self.token_count))

    @property
    def points(self):
        return (
            sum(card.points for cards in self.cards.values() for card in cards) +
            sum(noble.points for noble in self.nobles)
        )

    @property
    def discounts(self):
        return {token: len(cards) for token, cards in self.cards.items()}

    def card_cost(self, card):
        discounts = self.discounts
        return {token: max(0, amount - discounts[token]) for token, amount in card.cost.items()}

    def card_payment(self, card):
        """Use matching gems first, then gold for discounted cost shortfalls."""
        payment = {}
        gold = 0
        for token, amount in self.card_cost(card).items():
            matching = min(amount, self.tokens.get(token, 0))
            if matching:
                payment[token] = matching
            gold += amount - matching
        if gold:
            payment[GOLD] = gold
        return payment
