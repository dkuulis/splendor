class Noble:
    def __init__(self, noble_id, points, requirements):
        self.id = noble_id
        self.points = points
        self.requirements = dict(requirements)
