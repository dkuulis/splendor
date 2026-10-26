class Card:
    def __init__(self, card_id, tier, token, points, cost):
        self.id = card_id
        self.tier = tier
        self.token = token
        self.points = points
        self.cost = dict(cost)
