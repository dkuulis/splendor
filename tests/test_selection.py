import copy
import unittest

from game.constants import DIAMOND, SAPPHIRE, EMERALD, RUBY, ONYX, GOLD
from game import Card, State


class SelectionTests(unittest.TestCase):
    def setUp(self):
        self.state = State()
        self.card = Card('selected', 1, RUBY, 1, {})
        self.state.market[1] = [self.card]

    def test_selection_is_pending_and_mutually_exclusive(self):
        state = self.state
        supply = dict(state.supply)
        state.select_token(RUBY)
        state.select_card(self.card)
        self.assertEqual(state.selected_tokens, {})
        self.assertIs(state.selected_card, self.card)
        self.assertEqual(state.market[1], [self.card])
        for cards in state.players[0].cards.values():
            self.assertEqual(cards, [])
        self.assertEqual(state.turn.active_player, 0)
        self.assertEqual(state.log, [])
        state.select_token(SAPPHIRE)
        self.assertIsNone(state.selected_card)
        self.assertEqual(state.selected_tokens, {SAPPHIRE: 1})
        self.assertEqual(state.supply, supply)
        state.deselect_token(SAPPHIRE)
        self.assertEqual(state.selected_tokens, {})

    def test_card_toggle_and_replacement(self):
        other = Card('other', 1, ONYX, 0, {})
        self.state.market[1].append(other)
        self.state.select_card(self.card)
        self.state.select_card(other)
        self.assertIs(self.state.selected_card, other)
        self.state.select_card(other)
        self.assertIsNone(self.state.selected_card)

    def test_invalid_selection_preserves_pending_action(self):
        self.state.select_card(self.card)
        self.state.select_token('unknown')
        self.state.supply[RUBY] = 0
        self.state.select_token(RUBY)
        self.state.select_card(Card('missing', 1, RUBY, 0, {}))
        self.assertIs(self.state.selected_card, self.card)

    def test_gold_selection_blocks_action_until_deselected(self):
        state = self.state
        supply = dict(state.supply)
        state.select_token(GOLD)
        self.assertIsNone(state.selected_card)
        self.assertEqual(state.selected_tokens, {GOLD: 1})
        for replace_gems in (False, True):
            with self.subTest(replace_gems=replace_gems):
                if replace_gems:
                    state.select_token(RUBY)
                    state.select_token(SAPPHIRE)
                    state.select_token(GOLD)
                self.assertEqual(state.selected_tokens, {GOLD: 1})
                self.assertIsNotNone(state.action_error)
                with self.assertRaises(ValueError):
                    state.perform_action()
                self.assertEqual(state.supply, supply)
                self.assertEqual(state.current_player.tokens, {})
                self.assertEqual(state.turn.active_player, 0)
        state.deselect_token(GOLD)
        self.assertEqual(state.selected_tokens, {})
        self.assertIsNone(state.action_error)

    def test_non_gold_selection_clears_card_and_gold_but_keeps_other_gems(self):
        state = self.state
        state.select_card(self.card)
        state.select_token(GOLD)
        state.select_token(RUBY)
        self.assertIsNone(state.selected_card)
        self.assertEqual(state.selected_tokens, {RUBY: 1})
        state.select_token(SAPPHIRE)
        self.assertEqual(state.selected_tokens, {RUBY: 1, SAPPHIRE: 1})
        self.assertIsNone(state.action_error)

    def test_gold_preserves_selected_card_and_blocks_purchase(self):
        state = self.state
        state.select_card(self.card)
        state.select_token(GOLD)
        self.assertIs(state.selected_card, self.card)
        self.assertEqual(state.selected_tokens, {GOLD: 1})
        self.assertEqual(state.action_label, 'Reserve')
        self.assertIsNone(state.action_error)
        with self.assertRaises(ValueError):
            state.buy_card()
        self.assertEqual(state.market[1], [self.card])
        self.assertEqual(state.turn.active_player, 0)
        state.deselect_token(GOLD)
        self.assertIs(state.selected_card, self.card)
        self.assertIsNone(state.action_error)
        state.perform_action()
        self.assertIn(self.card, state.players[0].cards[self.card.token])

    def test_unaffordable_card_can_be_selected_and_deselected_but_not_bought(self):
        self.card.cost = {RUBY: 2}
        self.state.select_token(RUBY)
        self.state.select_card(self.card)
        self.assertIs(self.state.selected_card, self.card)
        self.assertEqual(self.state.selected_tokens, {})
        self.assertEqual(self.state.action_label, 'Buy')
        self.assertIsNotNone(self.state.action_error)
        with self.assertRaises(ValueError):
            self.state.perform_action()
        self.assertIs(self.state.selected_card, self.card)
        self.assertEqual(self.state.market[1], [self.card])
        self.assertEqual(self.state.turn.active_player, 0)
        self.assertEqual(self.state.log, [])
        self.state.select_card(self.card)
        self.assertIsNone(self.state.selected_card)

    def test_confirm_purchase_clears_selection_and_refills_slot(self):
        replacement = Card('replacement', 1, ONYX, 0, {})
        self.state.decks[1] = [replacement]
        self.state.select_card(self.card)
        self.assertEqual(self.state.action_label, 'Buy')
        self.assertIsNone(self.state.action_error)
        self.state.perform_action()
        self.assertIsNone(self.state.selected_card)
        self.assertEqual(self.state.selected_tokens, {})
        self.assertEqual(self.state.players[0].cards[self.card.token], [self.card])
        self.assertEqual(self.state.market[1], [replacement])
        self.assertEqual(self.state.turn.active_player, 1)
        self.assertEqual(self.state.action_label, 'Pass')

    def test_empty_selection_passes_even_at_token_limit(self):
        self.state.current_player.tokens = {RUBY: 10}
        self.assertEqual(self.state.action_label, 'Pass')
        self.assertIsNone(self.state.action_error)
        self.state.perform_action()
        self.assertEqual(self.state.log, ['YOU passed.'])
        self.assertEqual(self.state.turn.active_player, 1)

    def test_selected_gems_are_taken_in_one_turn(self):
        self.state.select_token(RUBY)
        self.state.select_token(DIAMOND)
        self.assertEqual(self.state.action_label, 'Take')
        self.assertIsNone(self.state.action_error)
        self.state.perform_action()
        self.assertEqual(self.state.players[0].tokens, {RUBY: 1, DIAMOND: 1})
        self.assertEqual(self.state.log, ['YOU took Diamond, Ruby.'])
        self.assertEqual(self.state.turn.active_player, 1)
        self.assertEqual(self.state.selected_tokens, {})
        self.assertEqual(self.state.action_label, 'Pass')

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
                    state.select_card(card)
                    if case == 'missing card':
                        state.market[1].clear()
                    elif case == 'unaffordable card':
                        card.cost = {RUBY: 1}
                elif case != 'finished pass':
                    state.select_token(RUBY)
                    if case == 'unavailable gem':
                        state.supply[RUBY] = 0
                    elif case == 'full inventory':
                        state.current_player.tokens = {DIAMOND: 10}
                    elif case == 'too many gems':
                        for token in (DIAMOND, ONYX, EMERALD):
                            state.select_token(token)
                if case.startswith('finished'):
                    state.turn.finished = True
                # Compare serialized model data so object identity is irrelevant.
                def snapshot():
                    return copy.deepcopy((state.supply, state.selected_tokens,
                                          state.selected_card.id if state.selected_card else None,
                                          [vars(player) for player in state.players],
                                          {tier: [item.id for item in row] for tier, row in state.market.items()},
                                          vars(state.turn), state.log))
                before = snapshot()
                error = state.action_error
                self.assertIsNotNone(error)
                self.assertEqual(snapshot(), before)
                with self.assertRaises(ValueError) as raised:
                    state.perform_action()
                self.assertEqual(str(raised.exception), error)
                self.assertEqual(snapshot(), before)

    def test_pass_and_take_clear_selection(self):
        self.state.select_card(self.card)
        self.state.pass_turn()
        self.assertIsNone(self.state.selected_card)
        self.state.select_token(RUBY)
        self.state.take_tokens()
        self.assertEqual(self.state.selected_tokens, {})

    def test_finished_game_cannot_select(self):
        self.state.turn.finished = True
        self.state.select_card(self.card)
        self.state.select_token(RUBY)
        self.assertIsNone(self.state.selected_card)
        self.assertEqual(self.state.selected_tokens, {})
