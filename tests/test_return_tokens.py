import unittest

from game import Card, State
from game.constants import DIAMOND, SAPPHIRE, EMERALD, RUBY, GOLD
from game.noble import Noble
from game.selection import Selection


class ReturnTokensTests(unittest.TestCase):
    def start_take(self, held, tokens):
        state = State()
        selection = Selection()
        state.current_player.tokens = dict(held)
        for token, amount in held.items():
            state.supply[token] -= amount
        selection.tokens = dict(tokens)
        self.assertTrue(selection.can_take_tokens(state))
        selection.perform_action(state)
        return state, selection

    def test_takes_from_eight_to_ten_defer_turn_until_exact_excess_returned(self):
        for held in range(8, 11):
            with self.subTest(held=held):
                state, selection = self.start_take(
                    {GOLD: 4, DIAMOND: 4, SAPPHIRE: held - 8},
                    {RUBY: 1, SAPPHIRE: 1, EMERALD: 1})
                player = state.current_player
                self.assertEqual(player.token_count, held + 3)
                self.assertEqual(state.turn.active_player, 0)
                self.assertTrue(state.return_required)
                self.assertEqual(selection.action_kind, 'return')
                self.assertEqual(selection.tokens, {})
                self.assertFalse(selection.can_perform_action(state))
                supply = dict(state.supply)
                for index in range(held - 7):
                    selection.select_return_token(GOLD, state)
                    self.assertEqual(selection.can_perform_action(state), index == held - 8)
                    self.assertEqual(player.token_count, held + 3)
                    self.assertEqual(state.supply, supply)
                selection.perform_action(state)
                self.assertEqual(player.token_count, 10)
                self.assertEqual(state.supply[GOLD], supply[GOLD] + held - 7)
                self.assertEqual(state.turn.active_player, 1)
                self.assertFalse(state.return_required)
                self.assertEqual(selection.action_kind, 'pass')
                self.assertEqual(selection.tokens, {})

    def test_matching_take_can_return_old_and_new_tokens(self):
        state, selection = self.start_take({GOLD: 5, DIAMOND: 4, SAPPHIRE: 1}, {RUBY: 2})
        selection.select_return_token(RUBY, state)
        selection.select_return_token(SAPPHIRE, state)
        self.assertTrue(selection.can_perform_action(state))
        selection.perform_action(state)
        self.assertEqual(state.players[0].tokens, {GOLD: 5, DIAMOND: 4, RUBY: 1})
        self.assertEqual(state.supply[RUBY], 3)
        self.assertEqual(state.supply[SAPPHIRE], 4)

    def test_owned_tokens_cannot_be_selected_for_return_outside_return_phase(self):
        state = State()
        selection = Selection()
        state.current_player.tokens = {GOLD: 1}
        self.assertFalse(selection.can_select_return_token(GOLD, state))
        selection.select_return_token(GOLD, state)
        self.assertEqual(selection.tokens, {})
        self.assertFalse(selection.can_return_tokens(state))

    def test_return_selection_limits_deselection_and_clear(self):
        state, selection = self.start_take({GOLD: 5, DIAMOND: 4}, {RUBY: 2})
        supply = dict(state.supply)
        for _ in range(3):
            selection.select_return_token(RUBY, state)
        self.assertEqual(selection.tokens, {RUBY: 2})
        self.assertFalse(selection.can_select_return_token(RUBY, state))
        self.assertFalse(selection.can_perform_action(state))
        selection.deselect_token(RUBY, state)
        self.assertEqual(selection.tokens, {RUBY: 1})
        self.assertTrue(selection.can_perform_action(state))
        selection.deselect_token(RUBY, state)
        self.assertEqual(selection.tokens, {})
        selection.select_return_token(GOLD, state)
        selection.deselect_token(GOLD, state)
        self.assertEqual(selection.tokens, {})
        selection.select_return_token('unknown', state)
        selection.select_return_token(EMERALD, state)
        self.assertEqual(selection.tokens, {})
        selection.select_return_token(GOLD, state)
        selection.clear()
        self.assertEqual(selection.action_kind, 'return')
        self.assertEqual(selection.tokens, {})
        self.assertEqual(state.supply, supply)
        for invalid in ({RUBY: 3}, {EMERALD: 1}, {'unknown': 1}, {RUBY: 0}, {RUBY: -1}):
            selection.tokens = invalid
            self.assertFalse(selection.can_return_tokens(state))

    def test_normal_actions_and_selection_are_disabled_during_return(self):
        state, selection = self.start_take({GOLD: 5, DIAMOND: 4}, {RUBY: 2})
        card = Card('free', 1, RUBY, 0, {})
        state.market[1] = [card]
        for permission in (selection.can_pass_turn(state), selection.can_take_tokens(state),
                           selection.can_buy_card(state), selection.can_reserve_card(state),
                           selection.can_select_card(card, state),
                           selection.can_select_token(RUBY, state), state.can_buy(card)):
            self.assertFalse(permission)
        selection.select_card(card, state)
        selection.reserve_card(card, state)
        selection.select_token(RUBY, state)
        self.assertIsNone(selection.card)
        self.assertEqual(selection.tokens, {})
        selection.select_return_token(GOLD, state)
        state.turn.finished = True
        self.assertFalse(selection.can_return_tokens(state))
        self.assertFalse(selection.can_select_return_token(RUBY, state))
        selection.deselect_token(GOLD, state)
        self.assertEqual(selection.tokens, {GOLD: 1})

    def test_reservation_at_ten_commits_card_gold_and_replacement_before_return(self):
        state = State()
        selection = Selection()
        player = state.current_player
        player.tokens = {DIAMOND: 4, SAPPHIRE: 4, GOLD: 2}
        card = Card('reserved', 1, RUBY, 1, {RUBY: 3})
        replacement = Card('replacement', 1, RUBY, 0, {})
        state.market[1] = [card]
        state.decks[1] = [replacement]
        selection.reserve_card(card, state)
        self.assertTrue(selection.can_perform_action(state))
        selection.perform_action(state)
        self.assertEqual(player.reserved_cards, [card])
        self.assertEqual(player.tokens[GOLD], 3)
        self.assertEqual(state.market[1], [replacement])
        self.assertEqual(state.turn.active_player, 0)
        self.assertEqual(selection.action_kind, 'return')
        selection.select_return_token(GOLD, state)
        selection.perform_action(state)
        self.assertEqual(player.token_count, 10)
        self.assertEqual(player.tokens[GOLD], 2)
        self.assertEqual(state.turn.active_player, 1)

    def test_nobles_and_game_completion_wait_for_return_on_both_players(self):
        for active in (0, 1):
            with self.subTest(active=active):
                state = State()
                selection = Selection()
                state.turn.active_player = active
                state.turn.consecutive_passes = 1
                player = state.current_player
                player.tokens = {GOLD: 5, DIAMOND: 4, SAPPHIRE: 1}
                player.add_card(Card('winning', 1, RUBY, 12, {}))
                nobles = [Noble('first', 3, {RUBY: 1}), Noble('second', 3, {RUBY: 1})]
                state.nobles = list(nobles)
                selection.tokens = {RUBY: 2}
                self.assertTrue(selection.can_perform_action(state))
                selection.perform_action(state)
                self.assertEqual(player.nobles, [])
                self.assertEqual(state.turn.consecutive_passes, 1)
                self.assertFalse(state.turn.final_round)
                self.assertFalse(state.turn.finished)
                self.assertEqual(state.turn.active_player, active)
                selection.select_return_token(RUBY, state)
                selection.select_return_token(RUBY, state)
                selection.perform_action(state)
                self.assertEqual(player.nobles, [nobles[0]])
                self.assertNotIn(RUBY, player.tokens)
                self.assertEqual(state.nobles, [nobles[1]])
                self.assertEqual(state.turn.consecutive_passes, 0)
                self.assertTrue(state.turn.final_round)
                self.assertEqual(state.turn.finished, active == 1)
                self.assertEqual(state.turn.active_player, 1)
                self.assertEqual(state.turn.round_number, 1)

    def test_state_return_uses_explicit_counts_without_changing_selection(self):
        state, selection = self.start_take({GOLD: 5, DIAMOND: 4}, {RUBY: 2})
        selection.select_return_token(GOLD, state)
        tokens = {RUBY: 1}
        state.return_tokens(tokens)
        self.assertEqual(tokens, {RUBY: 1})
        self.assertEqual(selection.tokens, {GOLD: 1})
        self.assertEqual(state.players[0].tokens[RUBY], 1)
        self.assertEqual(state.supply[RUBY], 3)
