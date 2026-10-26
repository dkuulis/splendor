from collections import Counter
import copy
from itertools import combinations
import unittest

from game.selection import Selection

from game.constants import GEMS, TOKENS, DIAMOND, SAPPHIRE, EMERALD, RUBY, ONYX, GOLD
from game import State


class TakeTokensTests(unittest.TestCase):
    def test_collection_uses_supplied_tokens_instead_of_pending_tokens(self):
        state = State()
        selection = Selection()
        selection.select_token(RUBY, state)
        tokens = {SAPPHIRE: 1}
        supply = dict(state.supply)
        state.take_tokens(tokens)
        self.assertEqual(state.players[0].tokens, {SAPPHIRE: 1})
        self.assertEqual(state.supply[RUBY], supply[RUBY])
        self.assertEqual(state.supply[SAPPHIRE], supply[SAPPHIRE] - 1)
        self.assertEqual(tokens, {SAPPHIRE: 1})
        self.assertEqual(selection.tokens, {RUBY: 1})

    def test_matching_gems_dispatch_transfers_two_and_clears_selection(self):
        state = State()
        selection = Selection()
        state.current_player.tokens = {GOLD: 8}
        selection.select_token(RUBY, state)
        selection.select_token(RUBY, state)
        self.assertTrue(selection.can_perform_action(state))
        selection.perform_action(state)
        self.assertEqual(state.players[0].tokens, {GOLD: 8, RUBY: 2})
        self.assertEqual(state.supply[RUBY], 2)
        self.assertEqual(selection.tokens, {})
        self.assertEqual(state.turn.active_player, 1)

    def test_empty_selection_passes_and_counts_toward_stalemate(self):
        state = State()
        selection = Selection()
        state.players[0].tokens = {RUBY: 10}
        supply = dict(state.supply)
        self.assertFalse(selection.can_take_tokens(state))
        selection.perform_action(state)
        self.assertEqual(state.players[0].tokens, {RUBY: 10})
        self.assertEqual(state.supply, supply)
        self.assertEqual(state.turn.active_player, 1)
        self.assertEqual(state.turn.consecutive_passes, 1)
        self.assertFalse(state.turn.finished)
        selection.perform_action(state)
        self.assertEqual(state.supply, supply)
        self.assertEqual(state.players[1].tokens, {})
        self.assertEqual(state.turn.consecutive_passes, 2)
        self.assertTrue(state.turn.finished)
        self.assertFalse(selection.can_take_tokens(state))

    def test_validation_matches_action_without_changing_state(self):
        cases = [
            ([RUBY], 0, 4, False, False),
            ([RUBY, ONYX, DIAMOND], 0, 4, False, True),
            ([], 0, 4, False, False),
            ([], 10, 4, False, False),
            ([], 0, 4, True, False),
            ([RUBY, RUBY], 0, 4, False, True),
            ([RUBY, RUBY], 0, 3, False, False),
            ([RUBY, RUBY], 8, 4, False, True),
            ([RUBY, RUBY], 9, 4, False, True),
            ([RUBY, RUBY], 10, 4, False, True),
            ([RUBY, RUBY, ONYX], 0, 4, False, False),
            ([RUBY, RUBY, RUBY], 0, 4, False, False),
            ([RUBY, ONYX, DIAMOND, EMERALD], 0, 4, False, False),
            ([GOLD], 0, 4, False, False),
            (['unknown'], 0, 4, False, False),
            ([RUBY], 0, 0, False, False),
            ([RUBY], 9, 4, False, False),
            ([RUBY, ONYX], 9, 4, False, False),
            ([RUBY], 10, 4, False, False),
            ([RUBY], 0, 4, True, False),
        ]
        for tokens, held, available, finished, expected in cases:
            with self.subTest(tokens=tokens, held=held, available=available, finished=finished):
                state = State()
                selection = Selection()
                state.current_player.tokens = {DIAMOND: held}
                state.supply[RUBY] = available
                state.turn.finished = finished
                before = copy.deepcopy((state.supply, state.current_player.tokens,
                                        vars(state.turn)))
                selection.tokens = dict(Counter(tokens))
                self.assertIs(selection.can_take_tokens(state), expected)
                self.assertEqual((state.supply, state.current_player.tokens,
                                  vars(state.turn)), before)
                if expected:
                    state.take_tokens(selection.tokens)

    def test_transfer_and_manual_second_player(self):
        state = State()
        selection = Selection()
        selection.tokens = {RUBY: 1, ONYX: 1, DIAMOND: 1}
        state.take_tokens(selection.tokens)
        self.assertEqual(state.players[0].tokens, {RUBY: 1, ONYX: 1, DIAMOND: 1})
        self.assertEqual(state.supply[RUBY], 3)
        self.assertEqual(state.turn.active_player, 1)
        selection.tokens = {RUBY: 1}
        state.take_tokens(selection.tokens)
        self.assertEqual(state.players[1].tokens, {RUBY: 1})
        self.assertEqual(state.supply[RUBY], 2)
        self.assertEqual(state.turn.active_player, 0)
        self.assertEqual(state.turn.round_number, 2)

    def test_disallowed_token_checks_leave_state_unchanged(self):
        for tokens in ([RUBY] * 3, [RUBY, ONYX, DIAMOND, EMERALD], [GOLD], [SAPPHIRE]):
            with self.subTest(tokens=tokens):
                state = State()
                selection = Selection()
                state.supply[SAPPHIRE] = 0
                before = copy.deepcopy((state.supply, state.players[0].tokens, vars(state.turn)))
                selection.tokens = dict(Counter(tokens))
                self.assertFalse(selection.can_take_tokens(state))
                self.assertEqual((state.supply, state.players[0].tokens, vars(state.turn)), before)

    def test_limit_and_pass_reset(self):
        state = State()
        selection = Selection()
        state.players[0].tokens = {RUBY: 9}
        selection.tokens = {ONYX: 2}
        self.assertTrue(selection.can_take_tokens(state))
        selection.tokens = {ONYX: 1}
        state.take_tokens(selection.tokens)
        self.assertEqual(sum(state.players[0].tokens.values()), 10)
        state.pass_turn()
        selection.tokens = {EMERALD: 2}
        self.assertTrue(selection.can_take_tokens(state))
        self.assertEqual(state.turn.consecutive_passes, 1)

        state = State()
        selection = Selection()
        state.pass_turn()
        selection.tokens = {RUBY: 1}
        state.take_tokens(selection.tokens)
        self.assertEqual(state.turn.consecutive_passes, 0)
        state.pass_turn()
        self.assertFalse(state.turn.finished)

    def test_finished_game_disables_take(self):
        state = State()
        selection = Selection()
        state.pass_turn()
        state.pass_turn()
        selection.tokens = {RUBY: 1}
        self.assertFalse(selection.can_take_tokens(state))
        self.assertEqual(state.players[1].tokens, {})

    def test_distinct_take_uses_all_available_colors_up_to_three_for_both_players(self):
        for is_ai in (False, True):
            for available_count in range(6):
                for size in range(1, 4):
                    for colors in combinations(GEMS, size):
                        state = State()
                        state.current_player.is_ai = is_ai
                        available = GEMS[:available_count]
                        state.supply = {token: int(token in available) for token in TOKENS}
                        state.supply[GOLD] = 5  # Gold is not an available gem color.
                        selection = Selection()
                        selection.tokens = {token: 1 for token in colors}
                        expected = size == min(3, available_count) and all(token in available for token in colors)
                        with self.subTest(is_ai=is_ai, available=available, colors=colors):
                            self.assertEqual(selection.can_take_tokens(state), expected)

    def test_scarce_take_can_overflow_and_return_before_advancing(self):
        state = State()
        state.current_player.tokens = {GOLD: 5, DIAMOND: 4, RUBY: 1}
        state.supply = {token: int(token in (SAPPHIRE, EMERALD)) for token in TOKENS}
        selection = Selection()
        selection.tokens = {SAPPHIRE: 1, EMERALD: 1}
        self.assertTrue(selection.can_perform_action(state))
        selection.perform_action(state)
        self.assertTrue(selection.returning)
        self.assertEqual(state.turn.active_player, 0)
        selection.tokens = {GOLD: 2}
        self.assertTrue(selection.can_perform_action(state))
        selection.perform_action(state)
        self.assertEqual(state.players[0].token_count, 10)
        self.assertEqual(state.turn.active_player, 1)

    def test_matching_pair_still_requires_four_in_supply_for_both_player_types(self):
        for is_ai in (False, True):
            for available in (2, 3, 4):
                with self.subTest(is_ai=is_ai, available=available):
                    state = State()
                    state.current_player.is_ai = is_ai
                    state.supply[RUBY] = available
                    selection = Selection()
                    selection.select_token(RUBY, state)
                    selection.select_token(RUBY, state)
                    self.assertEqual(selection.can_perform_action(state), available == 4)


if __name__ == '__main__':
    unittest.main()
