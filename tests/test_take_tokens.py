import copy
import unittest

from game import State


class TakeTokensTests(unittest.TestCase):
    def test_transfer_and_manual_second_player(self):
        state = State()
        state.take_tokens(['Ruby', 'Onyx', 'Diamond'])
        self.assertEqual(state.players[0].tokens, {'Ruby': 1, 'Onyx': 1, 'Diamond': 1})
        self.assertEqual(state.supply['Ruby'], 3)
        self.assertEqual(state.turn.active_player, 1)
        state.take_tokens(['Ruby'])
        self.assertEqual(state.players[1].tokens, {'Ruby': 1})
        self.assertEqual(state.supply['Ruby'], 2)
        self.assertEqual(state.turn.active_player, 0)
        self.assertEqual(state.turn.round_number, 2)
        self.assertEqual(len(state.log), 2)

    def test_invalid_moves_leave_state_unchanged(self):
        for tokens in ([], ['Ruby'] * 2, ['Ruby', 'Onyx', 'Diamond', 'Emerald'], ['Gold'], ['Sapphire']):
            with self.subTest(tokens=tokens):
                state = State()
                state.supply['Sapphire'] = 0
                before = copy.deepcopy((state.supply, state.players[0].tokens, vars(state.turn), state.log))
                with self.assertRaises(ValueError):
                    state.take_tokens(tokens)
                self.assertEqual((state.supply, state.players[0].tokens, vars(state.turn), state.log), before)

    def test_limit_and_pass_reset(self):
        state = State()
        state.players[0].tokens = {'Ruby': 9}
        with self.assertRaises(ValueError):
            state.take_tokens(['Onyx', 'Emerald'])
        state.take_tokens(['Onyx'])
        self.assertEqual(sum(state.players[0].tokens.values()), 10)
        state.pass_turn()
        with self.assertRaises(ValueError):
            state.take_tokens(['Onyx'])
        self.assertEqual(state.turn.consecutive_passes, 1)

        state = State()
        state.pass_turn()
        state.take_tokens(['Ruby'])
        self.assertEqual(state.turn.consecutive_passes, 0)
        state.pass_turn()
        self.assertFalse(state.turn.finished)

    def test_finished_game_rejects_take(self):
        state = State()
        state.pass_turn()
        state.pass_turn()
        with self.assertRaises(ValueError):
            state.take_tokens(['Ruby'])
        self.assertEqual(state.players[1].tokens, {})


if __name__ == '__main__':
    unittest.main()
