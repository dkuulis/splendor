class Noble:
    def __init__(self, noble_id, points, requirements=None):
        self.id = noble_id
        self.points = points
        self.requirements = dict(requirements) if requirements is not None else {}
