from collections import Counter
import copy
import unittest

from game.constants import DIAMOND, SAPPHIRE, EMERALD, RUBY, ONYX, GOLD
from game import State


class TakeTokensTests(unittest.TestCase):
    def test_taking_zero_keeps_inventory_and_counts_toward_stalemate(self):
        state = State()
        state.players[0].tokens = {RUBY: 10}
        supply = dict(state.supply)
        state.take_tokens()
        self.assertEqual(state.players[0].tokens, {RUBY: 10})
        self.assertEqual(state.supply, supply)
        self.assertEqual(state.turn.active_player, 1)
        self.assertEqual(state.turn.consecutive_passes, 1)
        self.assertFalse(state.turn.finished)
        state.take_tokens()
        self.assertEqual(state.supply, supply)
        self.assertEqual(state.players[1].tokens, {})
        self.assertEqual(state.turn.consecutive_passes, 2)
        self.assertTrue(state.turn.finished)
        with self.assertRaises(ValueError):
            state.take_tokens()

    def test_validation_matches_action_without_changing_state(self):
        cases = [
            ([RUBY], 0, 4, False, None),
            ([RUBY, ONYX, DIAMOND], 0, 4, False, None),
            ([], 0, 4, False, None),
            ([], 10, 4, False, None),
            ([], 0, 4, True, "The game has already ended."),
            ([RUBY, RUBY], 0, 4, False, "Select up to three different token types."),
            ([RUBY, ONYX, DIAMOND, EMERALD], 0, 4, False,
             "Select up to three different token types."),
            ([GOLD], 0, 4, False, "A selected gem is not available."),
            (['unknown'], 0, 4, False, "A selected gem is not available."),
            ([RUBY], 0, 0, False, "A selected gem is not available."),
            ([RUBY], 9, 4, False, None),
            ([RUBY, ONYX], 9, 4, False, "You cannot hold more than 10 gems."),
            ([RUBY], 10, 4, False, "You cannot hold more than 10 gems."),
            ([RUBY], 0, 4, True, "The game has already ended."),
        ]
        for tokens, held, available, finished, expected in cases:
            with self.subTest(tokens=tokens, held=held, available=available, finished=finished):
                state = State()
                state.current_player.tokens = {DIAMOND: held}
                state.supply[RUBY] = available
                state.turn.finished = finished
                before = copy.deepcopy((state.supply, state.current_player.tokens,
                                        vars(state.turn), state.log))
                state.selection.tokens = dict(Counter(tokens))
                self.assertEqual(state.take_tokens_error(), expected)
                self.assertEqual((state.supply, state.current_player.tokens,
                                  vars(state.turn), state.log), before)
                if expected is None:
                    state.take_tokens()
                else:
                    with self.assertRaises(ValueError) as error:
                        state.take_tokens()
                    self.assertEqual(str(error.exception), expected)

    def test_transfer_and_manual_second_player(self):
        state = State()
        state.selection.tokens = {RUBY: 1, ONYX: 1, DIAMOND: 1}
        state.take_tokens()
        self.assertEqual(state.players[0].tokens, {RUBY: 1, ONYX: 1, DIAMOND: 1})
        self.assertEqual(state.supply[RUBY], 3)
        self.assertEqual(state.turn.active_player, 1)
        state.selection.tokens = {RUBY: 1}
        state.take_tokens()
        self.assertEqual(state.players[1].tokens, {RUBY: 1})
        self.assertEqual(state.supply[RUBY], 2)
        self.assertEqual(state.turn.active_player, 0)
        self.assertEqual(state.turn.round_number, 2)
        self.assertEqual(len(state.log), 2)

    def test_invalid_moves_leave_state_unchanged(self):
        for tokens in ([RUBY] * 2, [RUBY, ONYX, DIAMOND, EMERALD], [GOLD], [SAPPHIRE]):
            with self.subTest(tokens=tokens):
                state = State()
                state.supply[SAPPHIRE] = 0
                before = copy.deepcopy((state.supply, state.players[0].tokens, vars(state.turn), state.log))
                with self.assertRaises(ValueError):
                    state.selection.tokens = dict(Counter(tokens))
                    state.take_tokens()
                self.assertEqual((state.supply, state.players[0].tokens, vars(state.turn), state.log), before)

    def test_limit_and_pass_reset(self):
        state = State()
        state.players[0].tokens = {RUBY: 9}
        with self.assertRaises(ValueError):
            state.selection.tokens = {ONYX: 1, EMERALD: 1}
            state.take_tokens()
        state.selection.tokens = {ONYX: 1}
        state.take_tokens()
        self.assertEqual(sum(state.players[0].tokens.values()), 10)
        state.pass_turn()
        with self.assertRaises(ValueError):
            state.selection.tokens = {ONYX: 1}
            state.take_tokens()
        self.assertEqual(state.turn.consecutive_passes, 1)

        state = State()
        state.pass_turn()
        state.selection.tokens = {RUBY: 1}
        state.take_tokens()
        self.assertEqual(state.turn.consecutive_passes, 0)
        state.pass_turn()
        self.assertFalse(state.turn.finished)

    def test_finished_game_rejects_take(self):
        state = State()
        state.pass_turn()
        state.pass_turn()
        with self.assertRaises(ValueError):
            state.selection.tokens = {RUBY: 1}
            state.take_tokens()
        self.assertEqual(state.players[1].tokens, {})


if __name__ == '__main__':
    unittest.main()
