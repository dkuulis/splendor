class Card:
    def __init__(self, card_id, tier, color, points, cost=None):
        self.id = card_id
        self.tier = tier
        self.color = color
        self.points = points
        self.cost = dict(cost) if cost is not None else {}
