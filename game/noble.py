class Noble:
    def __init__(self, noble_id, points, requirements):
        self.id = noble_id
        self.points = points
        self.requirements = dict(requirements)


def assign_noble(player, nobles):
    """Award the first qualifying noble and return a log message, or None."""
    discounts = player.discounts
    for noble in nobles:
        if all(discounts[token] >= count for token, count in noble.requirements.items()):
            nobles.remove(noble)
            player.nobles.append(noble)
            return f"{player.name} received noble for {noble.points} points."
    return None
