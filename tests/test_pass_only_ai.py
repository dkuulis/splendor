import unittest

from game import State
from ai.pass_only import PassOnlyAI


class PassOnlyAITests(unittest.TestCase):
    def test_strategy_passes_once(self):
        state = State()
        state.turn.active_player = 1
        PassOnlyAI().play_turn(state)
        self.assertEqual(state.turn.active_player, 0)
        self.assertEqual(state.turn.consecutive_passes, 1)
        self.assertEqual(state.log, ['COMPUTER passed.'])

    def test_two_passes_end_game(self):
        state = State()
        state.pass_turn()
        PassOnlyAI().play_turn(state)
        self.assertTrue(state.turn.finished)
        self.assertIsNone(state.turn.winner)


if __name__ == '__main__':
    unittest.main()
