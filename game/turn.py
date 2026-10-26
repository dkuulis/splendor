class Turn:
    def __init__(self):
        self.active_player = 0
        self.round_number = 1
        self.consecutive_passes = 0
        self.final_round = False
        self.finished = False
        self.winner = None  # None also means a draw when finished.
