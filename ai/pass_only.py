class PassOnlyAI:
    """Minimal strategy: always use the legal pass action."""

    def play_turn(self, state):
        state.clear_selection()
        state.perform_action()
