import copy
import unittest

from game.constants import DIAMOND, SAPPHIRE, EMERALD, RUBY, ONYX, GOLD
from game import Card, State


class SelectionActionTests(unittest.TestCase):
    def setUp(self):
        self.state = State()
        self.card = Card('selected', 1, RUBY, 1, {})
        self.state.market[1] = [self.card]

    def test_gold_selection_blocks_action_until_deselected(self):
        state = self.state
        supply = dict(state.supply)
        state.selection.select_token(GOLD, state)
        self.assertIsNone(state.selection.card)
        self.assertEqual(state.selection.tokens, {GOLD: 1})
        for replace_gems in (False, True):
            with self.subTest(replace_gems=replace_gems):
                if replace_gems:
                    state.selection.select_token(RUBY, state)
                    state.selection.select_token(SAPPHIRE, state)
                    state.selection.select_token(GOLD, state)
                self.assertEqual(state.selection.tokens, {GOLD: 1})
                self.assertIsNotNone(state.action_error)
                with self.assertRaises(ValueError):
                    state.perform_action()
                self.assertEqual(state.supply, supply)
                self.assertEqual(state.current_player.tokens, {})
                self.assertEqual(state.turn.active_player, 0)
        state.selection.deselect_token(GOLD, state)
        self.assertEqual(state.selection.tokens, {})
        self.assertIsNone(state.action_error)

    def test_gold_preserves_selected_card_and_blocks_purchase(self):
        state = self.state
        state.selection.select_card(self.card, state)
        state.selection.select_token(GOLD, state)
        self.assertIs(state.selection.card, self.card)
        self.assertEqual(state.selection.tokens, {GOLD: 1})
        self.assertEqual(state.selection.action_kind.capitalize(), 'Reserve')
        self.assertIsNone(state.action_error)
        with self.assertRaises(ValueError):
            state.buy_card()
        self.assertEqual(state.market[1], [self.card])
        self.assertEqual(state.turn.active_player, 0)
        state.selection.deselect_token(GOLD, state)
        self.assertIs(state.selection.card, self.card)
        self.assertIsNone(state.action_error)
        state.perform_action()
        self.assertIn(self.card, state.players[0].cards[self.card.token])

    def test_unaffordable_market_card_selects_gold_and_can_be_reserved(self):
        state = self.state
        self.card.cost = {RUBY: 2}
        supply = dict(state.supply)
        state.selection.select_token(RUBY, state)
        state.selection.select_card(self.card, state)
        self.assertIs(state.selection.card, self.card)
        self.assertEqual(state.selection.tokens, {GOLD: 1})
        self.assertEqual(state.selection.action_kind, 'reserve')
        self.assertIsNone(state.action_error)
        self.assertEqual(state.supply, supply)
        self.assertEqual(state.current_player.tokens, {})
        with self.assertRaises(ValueError):
            state.buy_card()
        state.selection.select_card(self.card, state)
        self.assertIsNone(state.selection.card)
        self.assertEqual(state.selection.action_kind, 'pass')
        state.selection.select_card(self.card, state)
        state.perform_action()
        self.assertEqual(state.players[0].reserved_cards, [self.card])
        self.assertEqual(state.players[0].tokens, {GOLD: 1})
        self.assertEqual(state.supply[GOLD], supply[GOLD] - 1)
        self.assertEqual(state.turn.active_player, 1)

    def test_automatic_reservation_still_checks_supply_and_limits(self):
        for case in ('no gold', 'full inventory', 'full reservations'):
            with self.subTest(case=case):
                state = State()
                card = Card('costly', 1, RUBY, 1, {SAPPHIRE: 2})
                state.market[1] = [card]
                if case == 'no gold':
                    state.supply[GOLD] = 0
                elif case == 'full inventory':
                    state.current_player.tokens = {RUBY: 10}
                else:
                    state.current_player.reserved_cards = [
                        Card(str(i), 1, RUBY, 0, {}) for i in range(3)]
                state.selection.select_card(card, state)
                self.assertEqual(state.selection.action_kind, 'reserve')
                self.assertEqual(state.selection.tokens, {GOLD: 1})
                error = state.action_error
                self.assertIsNotNone(error)
                before = copy.deepcopy((state.supply, state.current_player.tokens,
                                        vars(state.turn)))
                reserved = list(state.current_player.reserved_cards)
                with self.assertRaisesRegex(ValueError, error):
                    state.perform_action()
                self.assertEqual((state.supply, state.current_player.tokens,
                                  vars(state.turn)), before)
                self.assertEqual(state.current_player.reserved_cards, reserved)

    def test_confirm_purchase_clears_selection_and_refills_slot(self):
        replacement = Card('replacement', 1, ONYX, 0, {})
        self.state.decks[1] = [replacement]
        self.state.selection.select_card(self.card, self.state)
        self.assertEqual(self.state.selection.action_kind.capitalize(), 'Buy')
        self.assertIsNone(self.state.action_error)
        self.state.perform_action()
        self.assertIsNone(self.state.selection.card)
        self.assertEqual(self.state.selection.tokens, {})
        self.assertEqual(self.state.players[0].cards[self.card.token], [self.card])
        self.assertEqual(self.state.market[1], [replacement])
        self.assertEqual(self.state.turn.active_player, 1)
        self.assertEqual(self.state.selection.action_kind.capitalize(), 'Pass')

    def test_empty_selection_passes_even_at_token_limit(self):
        self.state.current_player.tokens = {RUBY: 10}
        self.assertEqual(self.state.selection.action_kind.capitalize(), 'Pass')
        self.assertIsNone(self.state.action_error)
        self.state.perform_action()
        self.assertEqual(self.state.players[0].tokens, {RUBY: 10})
        self.assertEqual(self.state.turn.consecutive_passes, 1)
        self.assertEqual(self.state.turn.active_player, 1)

    def test_selected_gems_are_taken_in_one_turn(self):
        self.state.selection.select_token(RUBY, self.state)
        self.state.selection.select_token(DIAMOND, self.state)
        self.assertEqual(self.state.selection.action_kind.capitalize(), 'Take')
        self.assertIsNone(self.state.action_error)
        self.state.perform_action()
        self.assertEqual(self.state.players[0].tokens, {RUBY: 1, DIAMOND: 1})
        self.assertEqual(self.state.turn.active_player, 1)
        self.assertEqual(self.state.selection.tokens, {})
        self.assertEqual(self.state.selection.action_kind.capitalize(), 'Pass')

    def test_invalid_actions_report_same_error_and_preserve_state(self):
        cases = ('missing card', 'unaffordable card', 'unavailable gem',
                 'too many gems', 'full inventory', 'finished pass',
                 'finished take', 'finished buy')
        for case in cases:
            with self.subTest(case=case):
                state = State()
                card = Card('selected', 1, RUBY, 1, {})
                state.market[1] = [card]
                if case in ('missing card', 'unaffordable card', 'finished buy'):
                    state.selection.select_card(card, state)
                    if case == 'missing card':
                        state.market[1].clear()
                    elif case == 'unaffordable card':
                        card.cost = {RUBY: 1}
                elif case != 'finished pass':
                    state.selection.select_token(RUBY, state)
                    if case == 'unavailable gem':
                        state.supply[RUBY] = 0
                    elif case == 'full inventory':
                        state.current_player.tokens = {DIAMOND: 10}
                    elif case == 'too many gems':
                        for token in (DIAMOND, ONYX, EMERALD):
                            state.selection.select_token(token, state)
                if case.startswith('finished'):
                    state.turn.finished = True
                # Compare serialized model data so object identity is irrelevant.
                def snapshot():
                    return copy.deepcopy((state.supply, state.selection.tokens,
                                          state.selection.action_kind,
                                          state.selection.card.id if state.selection.card else None,
                                          [vars(player) for player in state.players],
                                          {tier: [item.id for item in row] for tier, row in state.market.items()},
                                          vars(state.turn)))
                before = snapshot()
                error = state.action_error
                self.assertIsNotNone(error)
                self.assertEqual(snapshot(), before)
                with self.assertRaises(ValueError) as raised:
                    state.perform_action()
                self.assertEqual(str(raised.exception), error)
                self.assertEqual(snapshot(), before)

    def test_pass_and_take_clear_selection(self):
        self.state.selection.select_card(self.card, self.state)
        self.state.pass_turn()
        self.assertIsNone(self.state.selection.card)
        self.state.selection.select_token(RUBY, self.state)
        self.state.take_tokens()
        self.assertEqual(self.state.selection.tokens, {})
