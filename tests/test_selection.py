import unittest

from game.constants import SAPPHIRE, RUBY, ONYX, GOLD
from game import Card, State
from game.selection import Selection


class SelectionTests(unittest.TestCase):
    def setUp(self):
        self.state = State()
        self.card = Card('selected', 1, RUBY, 1, {})
        self.state.market[1] = [self.card]

    def test_selection_is_pending_and_mutually_exclusive(self):
        state = self.state
        supply = dict(state.supply)
        state.selection.select_token(RUBY, state)
        state.selection.select_card(self.card, state)
        self.assertEqual(state.selection.tokens, {})
        self.assertIs(state.selection.card, self.card)
        self.assertEqual(state.market[1], [self.card])
        for cards in state.players[0].cards.values():
            self.assertEqual(cards, [])
        self.assertEqual(state.turn.active_player, 0)
        self.assertEqual(state.log, [])
        state.selection.select_token(SAPPHIRE, state)
        self.assertIsNone(state.selection.card)
        self.assertEqual(state.selection.tokens, {SAPPHIRE: 1})
        self.assertEqual(state.supply, supply)
        state.selection.deselect_token(SAPPHIRE, state)
        self.assertEqual(state.selection.tokens, {})

    def test_card_toggle_and_replacement(self):
        other = Card('other', 1, ONYX, 0, {})
        self.state.market[1].append(other)
        self.state.selection.select_card(self.card, self.state)
        self.state.selection.select_card(other, self.state)
        self.assertIs(self.state.selection.card, other)
        self.state.selection.select_card(other, self.state)
        self.assertIsNone(self.state.selection.card)

    def test_invalid_selection_preserves_pending_action(self):
        self.state.selection.select_card(self.card, self.state)
        self.state.selection.select_token('unknown', self.state)
        self.state.supply[RUBY] = 0
        self.state.selection.select_token(RUBY, self.state)
        self.state.selection.select_card(Card('missing', 1, RUBY, 0, {}), self.state)
        self.assertIs(self.state.selection.card, self.card)

    def test_non_gold_selection_clears_card_and_gold_but_keeps_other_gems(self):
        state = self.state
        state.selection.select_card(self.card, state)
        state.selection.select_token(GOLD, state)
        state.selection.select_token(RUBY, state)
        self.assertIsNone(state.selection.card)
        self.assertEqual(state.selection.tokens, {RUBY: 1})
        state.selection.select_token(SAPPHIRE, state)
        self.assertEqual(state.selection.tokens, {RUBY: 1, SAPPHIRE: 1})
        self.assertIsNone(state.action_error)

    def test_finished_game_cannot_select(self):
        self.state.turn.finished = True
        self.state.selection.select_card(self.card, self.state)
        self.state.selection.select_token(RUBY, self.state)
        self.assertIsNone(self.state.selection.card)
        self.assertEqual(self.state.selection.tokens, {})

    def test_clear_resets_pending_action_even_after_game_ends(self):
        state = self.state
        selection = state.selection
        selection.select_card(self.card, state)
        selection.select_token(GOLD, state)
        state.turn.finished = True
        selection.clear()
        self.assertIsNone(selection.card)
        self.assertEqual(selection.tokens, {})
        self.assertEqual(selection.action_kind, 'pass')
        self.assertEqual(state.market[1], [self.card])
        self.assertEqual(state.current_player.tokens, {})

    def test_finished_game_preserves_pending_selection_on_deselect(self):
        state = self.state
        state.selection.select_token(RUBY, state)
        state.turn.finished = True
        state.selection.deselect_token(RUBY, state)
        self.assertEqual(state.selection.tokens, {RUBY: 1})

    def test_independent_selection_uses_supplied_state_without_changing_its_selection(self):
        state = self.state
        selection = Selection()
        selection.select_card(self.card, state)
        selection.select_token(GOLD, state)
        self.assertEqual(selection.action_kind, 'reserve')
        self.assertIsNone(state.selection.card)
        self.assertEqual(state.selection.tokens, {})
        self.assertEqual(state.current_player.tokens, {})
        self.assertEqual(state.market[1], [self.card])

    def test_card_methods_switch_intent_without_toggling_the_card_off(self):
        state = self.state
        selection = state.selection
        selection.select_card(self.card, state)
        self.assertEqual(selection.action_kind, 'buy')
        selection.reserve_card(self.card, state)
        self.assertEqual(selection.action_kind, 'reserve')
        self.assertIs(selection.card, self.card)
        self.assertEqual(selection.tokens, {GOLD: 1})
        selection.select_card(self.card, state)
        self.assertEqual(selection.action_kind, 'buy')
        self.assertIs(selection.card, self.card)
        self.assertEqual(selection.tokens, {})
        selection.select_card(self.card, state)
        self.assertEqual(selection.action_kind, 'pass')

    def test_reservation_replaces_and_toggles_cards(self):
        state = self.state
        other = Card('other', 1, ONYX, 0, {})
        state.market[1].append(other)
        selection = state.selection
        selection.reserve_card(self.card, state)
        selection.reserve_card(other, state)
        self.assertIs(selection.card, other)
        self.assertEqual(selection.action_kind, 'reserve')
        self.assertEqual(selection.tokens, {GOLD: 1})
        selection.reserve_card(other, state)
        self.assertEqual(selection.action_kind, 'pass')
        self.assertIsNone(selection.card)
        self.assertEqual(selection.tokens, {})

    def test_token_transitions_follow_action_kind(self):
        state = self.state
        selection = state.selection
        selection.select_token(GOLD, state)
        self.assertEqual(selection.action_kind, 'reserve')
        self.assertIsNotNone(state.action_error)
        selection.select_token(GOLD, state)
        self.assertEqual(selection.tokens, {GOLD: 1})
        selection.reserve_card(self.card, state)
        self.assertEqual(selection.action_kind, 'reserve')
        selection.deselect_token(GOLD, state)
        self.assertEqual(selection.action_kind, 'buy')
        self.assertIs(selection.card, self.card)
        selection.select_token(RUBY, state)
        selection.select_token(SAPPHIRE, state)
        self.assertEqual(selection.action_kind, 'take')
        self.assertIsNone(selection.card)
        selection.deselect_token(RUBY, state)
        self.assertEqual(selection.action_kind, 'take')
        selection.deselect_token(SAPPHIRE, state)
        self.assertEqual(selection.action_kind, 'pass')
        selection.select_token(GOLD, state)
        selection.deselect_token(GOLD, state)
        self.assertEqual(selection.action_kind, 'pass')

    def test_invalid_reservation_preserves_pending_buy(self):
        state = self.state
        selection = state.selection
        selection.select_card(self.card, state)
        reserved = Card('reserved', 1, RUBY, 0, {})
        state.current_player.reserved_cards.append(reserved)
        for card in (reserved, Card('missing', 1, RUBY, 0, {})):
            selection.reserve_card(card, state)
            self.assertEqual(selection.action_kind, 'buy')
            self.assertIs(selection.card, self.card)
            self.assertEqual(selection.tokens, {})
        state.turn.finished = True
        selection.reserve_card(self.card, state)
        self.assertEqual(selection.action_kind, 'buy')
