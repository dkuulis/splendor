import unittest

from game.selection import Selection

from game.constants import DIAMOND, RUBY
from game import Card, State


class PassTests(unittest.TestCase):
    def test_pass_switches_player_without_changing_inventory(self):
        state = State()
        state.players[0].tokens = {RUBY: 2}
        state.pass_turn()
        self.assertEqual(state.turn.active_player, 1)
        self.assertEqual(state.turn.consecutive_passes, 1)
        self.assertFalse(state.turn.finished)
        self.assertEqual(state.players[0].tokens, {RUBY: 2})
        self.assertEqual(state.supply[RUBY], 4)

    def test_two_passes_end_in_draw_and_disable_further_moves(self):
        state = State()
        selection = Selection()
        state.pass_turn()
        state.pass_turn()
        self.assertTrue(state.turn.finished)
        self.assertIsNone(state.turn.winner)
        self.assertFalse(selection.can_pass_turn(state))
        self.assertEqual(state.turn.consecutive_passes, 2)

    def test_points_then_fewer_cards_decide_winner(self):
        for points, expected in ((3, 0), (2, 1)):
            with self.subTest(points=points):
                state = State()
                state.players[0].add_card(Card('a', 1, RUBY, points, {}))
                state.players[0].add_card(Card('b', 1, RUBY, 0, {}))
                state.players[1].add_card(Card('c', 1, DIAMOND, 2, {}))
                state.pass_turn()
                state.pass_turn()
                self.assertEqual(state.turn.winner, expected)

    def test_final_round_waits_for_second_player(self):
        state = State()
        state.players[0].add_card(Card('a', 3, RUBY, 15, {}))
        state.pass_turn()
        self.assertTrue(state.turn.final_round)
        self.assertFalse(state.turn.finished)
        state.pass_turn()
        self.assertTrue(state.turn.finished)
        self.assertEqual(state.turn.winner, 0)


if __name__ == '__main__':
    unittest.main()
