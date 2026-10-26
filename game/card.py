class Card:
    def __init__(self, card_id, tier, token, points, cost=None):
        self.id = card_id
        self.tier = tier
        self.token = token
        self.points = points
        self.cost = dict(cost) if cost is not None else {}
