"""One-move greedy search over the compact simulation model."""

from .simulation_search import evaluate, make_selection


class GreedySimAI:
    """Choose the move with the best resulting greedy evaluation."""

    def make_selection(self, state, selection):
        make_selection(state, selection, evaluate)
