class PassOnlyAI:
    """Minimal strategy: leave an empty selection for Pass."""

    def make_selection(self, state, selection):
        selection.clear()
