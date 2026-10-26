class PassOnlyAI:
    """Minimal strategy: always use the legal pass action."""

    def play_turn(self, state):
        state.selection.clear()
        state.perform_action()
