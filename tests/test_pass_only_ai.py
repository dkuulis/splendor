import unittest

from game.selection import Selection

from game.constants import RUBY
from game import State
from ai.pass_only import PassOnlyAI


class PassOnlyAITests(unittest.TestCase):
    def test_strategy_selects_pass_without_executing(self):
        state = State()
        selection = Selection()
        state.turn.active_player = 1
        selection.select_token(RUBY, state)
        PassOnlyAI().make_selection(state, selection)
        self.assertEqual(state.turn.active_player, 1)
        self.assertEqual(state.turn.consecutive_passes, 0)
        self.assertEqual(selection.action_kind, 'pass')
        self.assertEqual(state.players[1].tokens, {})
        self.assertEqual(selection.tokens, {})

    def test_two_passes_end_game(self):
        state = State()
        selection = Selection()
        state.pass_turn()
        PassOnlyAI().make_selection(state, selection)
        self.assertFalse(state.turn.finished)
        self.assertEqual(state.turn.consecutive_passes, 1)
        self.assertEqual(selection.action_kind, 'pass')
        selection.perform_action(state)
        self.assertTrue(state.turn.finished)
        self.assertIsNone(state.turn.winner)


if __name__ == '__main__':
    unittest.main()
