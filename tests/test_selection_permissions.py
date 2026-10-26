import unittest

from game import Card, State
from game.constants import GOLD, RUBY, SAPPHIRE
from game.selection import Selection


class SelectionPermissionTests(unittest.TestCase):
    def setUp(self):
        self.state = State()
        self.selection = Selection()
        self.card = Card('market', 1, RUBY, 0, {})
        self.costly = Card('costly', 1, RUBY, 0, {RUBY: 2})
        self.reserved = Card('reserved', 1, RUBY, 0, {RUBY: 1})
        self.state.market[1] = [self.card, self.costly]
        self.state.current_player.reserved_cards = [self.reserved]

    def test_card_permissions_allow_market_cards_and_only_affordable_reserved(self):
        state = self.state
        selection = self.selection
        self.assertIs(selection.can_select_card(self.card, state), True)
        self.assertIs(selection.can_select_card(self.costly, state), True)
        self.assertIs(selection.can_select_card(self.reserved, state), False)
        self.assertIs(selection.can_select_card(None, state), False)
        state.current_player.tokens = {RUBY: 1}
        self.assertIs(selection.can_select_card(self.reserved, state), True)
        selection.select_card(self.reserved, state)
        state.current_player.tokens.clear()
        # Even if holdings change, the selected reserved card can be removed.
        self.assertIs(selection.can_select_card(self.reserved, state), True)
        selection.select_card(self.reserved, state)
        self.assertEqual(selection.action_kind, 'pass')

    def test_gold_permissions_follow_market_card_affordability(self):
        state = self.state
        selection = self.selection
        self.assertIs(selection.can_select_token(GOLD, state), False)
        self.assertIs(selection.can_deselect_token(GOLD, state), False)
        selection.select_card(self.card, state)
        self.assertIs(selection.can_select_token(GOLD, state), True)
        selection.select_token(GOLD, state)
        self.assertIs(selection.can_deselect_token(GOLD, state), True)
        selection.select_card(self.costly, state)
        self.assertIs(selection.can_select_token(GOLD, state), False)
        self.assertIs(selection.can_deselect_token(GOLD, state), False)
        state.current_player.tokens = {RUBY: 2}
        self.assertIs(selection.can_deselect_token(GOLD, state), True)
        selection.deselect_token(GOLD, state)
        state.supply[GOLD] = 0
        self.assertIs(selection.can_select_token(GOLD, state), False)

    def test_multiple_gold_selection_only_allows_reserving_with_one(self):
        state = self.state
        selection = self.selection
        selection.select_card(self.card, state)
        supply = dict(state.supply)
        for count in range(1, 6):
            selection.select_token(GOLD, state)
            self.assertEqual(selection.tokens, {GOLD: count})
            self.assertIs(selection.can_reserve_card(state), count == 1)
            self.assertIs(selection.can_perform_action(state), count == 1)
        self.assertFalse(selection.can_select_token(GOLD, state))
        selection.select_token(GOLD, state)
        self.assertEqual(selection.tokens, {GOLD: 5})
        for count in range(4, -1, -1):
            selection.deselect_token(GOLD, state)
            self.assertEqual(selection.tokens, {GOLD: count} if count else {})
            self.assertIs(selection.card, self.card)
            self.assertIs(selection.can_reserve_card(state), count == 1)
            self.assertIs(selection.can_perform_action(state), count <= 1)
        self.assertEqual(selection.action_kind, 'buy')
        self.assertEqual(state.supply, supply)
        self.assertEqual(state.current_player.tokens, {})

    def test_selection_can_be_allowed_while_confirmation_is_disallowed(self):
        for limit in ('gold supply', 'reservations'):
            with self.subTest(limit=limit):
                state = State()
                selection = Selection()
                state.market[1] = [self.costly]
                if limit == 'gold supply':
                    state.supply[GOLD] = 0
                else:
                    state.current_player.reserved_cards = [self.reserved] * 3
                self.assertIs(selection.can_select_card(self.costly, state), True)
                selection.select_card(self.costly, state)
                self.assertIs(selection.can_reserve_card(state), False)
                self.assertIs(selection.can_perform_action(state), False)
                self.assertIs(selection.card, self.costly)
                self.assertEqual(selection.tokens, {GOLD: 1})

    def test_permissions_use_this_selection_without_mutating_state(self):
        state = self.state
        supply = dict(state.supply)
        selection = Selection()
        selection.select_card(self.card, state)
        self.assertIs(selection.can_buy_card(state), True)
        self.assertIs(selection.can_take_tokens(state), False)
        self.assertIs(selection.can_perform_action(state), True)
        selection.select_token(GOLD, state)
        self.assertIs(selection.can_buy_card(state), False)
        self.assertIs(selection.can_reserve_card(state), True)
        self.assertIs(selection.can_perform_action(state), True)
        self.assertIsNone(self.selection.card)
        self.assertEqual(self.selection.tokens, {})
        self.assertEqual(state.current_player.tokens, {})
        self.assertEqual(state.market[1], [self.card, self.costly])
        self.assertEqual(state.supply, supply)
        self.assertEqual(state.turn.active_player, 0)

    def test_gem_selection_and_confirmation_allow_full_inventory(self):
        state = self.state
        selection = self.selection
        state.current_player.tokens = {SAPPHIRE: 10}
        self.assertIs(selection.can_select_token(RUBY, state), True)
        self.assertIs(selection.can_select_token('unknown', state), False)
        selection.select_token(RUBY, state)
        selection.select_token(RUBY, state)
        self.assertIs(selection.can_deselect_token(RUBY, state), True)
        self.assertIs(selection.can_take_tokens(state), True)
        selection.deselect_token(RUBY, state)
        selection.deselect_token(RUBY, state)
        self.assertIs(selection.can_perform_action(state), True)
        state.supply[RUBY] = 0
        self.assertIs(selection.can_select_token(RUBY, state), False)

    def test_finished_game_disables_all_permissions(self):
        state = self.state
        selection = self.selection
        selection.select_card(self.card, state)
        selection.select_token(GOLD, state)
        state.turn.finished = True
        for allowed in (
                selection.can_select_card(self.card, state),
                selection.can_select_token(RUBY, state),
                selection.can_deselect_token(GOLD, state),
                selection.can_pass_turn(state),
                selection.can_take_tokens(state),
                selection.can_buy_card(state),
                selection.can_reserve_card(state),
                selection.can_perform_action(state)):
            self.assertIs(allowed, False)
