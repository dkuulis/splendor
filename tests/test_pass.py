import unittest

from game import Card, State


class PassTests(unittest.TestCase):
    def test_pass_switches_player_without_changing_inventory(self):
        state = State()
        state.players[0].tokens = {'Ruby': 2}
        state.pass_turn()
        self.assertEqual(state.turn.active_player, 1)
        self.assertEqual(state.turn.consecutive_passes, 1)
        self.assertFalse(state.turn.finished)
        self.assertEqual(state.players[0].tokens, {'Ruby': 2})
        self.assertEqual(state.supply['Ruby'], 4)

    def test_two_passes_end_in_draw_and_reject_further_moves(self):
        state = State()
        state.pass_turn()
        state.pass_turn()
        self.assertTrue(state.turn.finished)
        self.assertIsNone(state.turn.winner)
        with self.assertRaises(ValueError):
            state.pass_turn()
        self.assertEqual(state.turn.consecutive_passes, 2)

    def test_points_then_fewer_cards_decide_winner(self):
        for points, expected in ((3, 0), (2, 1)):
            with self.subTest(points=points):
                state = State()
                state.players[0].cards = {
                    'a': Card('a', 1, 'Ruby', points),
                    'b': Card('b', 1, 'Onyx', 0),
                }
                state.players[1].cards = {'c': Card('c', 1, 'Diamond', 2)}
                state.pass_turn()
                state.pass_turn()
                self.assertEqual(state.turn.winner, expected)

    def test_final_round_waits_for_second_player(self):
        state = State()
        state.players[0].cards = {'a': Card('a', 3, 'Ruby', 15)}
        state.pass_turn()
        self.assertTrue(state.turn.final_round)
        self.assertFalse(state.turn.finished)
        state.pass_turn()
        self.assertTrue(state.turn.finished)
        self.assertEqual(state.turn.winner, 0)


if __name__ == '__main__':
    unittest.main()
