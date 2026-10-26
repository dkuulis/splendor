import unittest

from game import Card, State


class SelectionTests(unittest.TestCase):
    def setUp(self):
        self.state = State()
        self.card = Card('selected', 1, 'Ruby', 1)
        self.state.market[1] = [self.card]

    def test_selection_is_pending_and_mutually_exclusive(self):
        state = self.state
        supply = dict(state.supply)
        state.select_token('Ruby')
        state.select_card(self.card)
        self.assertEqual(state.selected_tokens, {})
        self.assertIs(state.selected_card, self.card)
        self.assertEqual(state.market[1], [self.card])
        self.assertEqual(state.players[0].cards, {})
        self.assertEqual(state.turn.active_player, 0)
        self.assertEqual(state.log, [])
        state.select_token('Sapphire')
        self.assertIsNone(state.selected_card)
        self.assertEqual(state.selected_tokens, {'Sapphire': 1})
        self.assertEqual(state.supply, supply)
        state.deselect_token('Sapphire')
        self.assertEqual(state.selected_tokens, {})

    def test_card_toggle_and_replacement(self):
        other = Card('other', 1, 'Onyx', 0)
        self.state.market[1].append(other)
        self.state.select_card(self.card)
        self.state.select_card(other)
        self.assertIs(self.state.selected_card, other)
        self.state.select_card(other)
        self.assertIsNone(self.state.selected_card)

    def test_invalid_selection_preserves_pending_action(self):
        self.state.select_card(self.card)
        self.state.select_token('Gold')
        self.state.select_token('unknown')
        self.state.supply['Ruby'] = 0
        self.state.select_token('Ruby')
        costly = Card('costly', 1, 'Ruby', 0, {'Ruby': 2})
        self.state.market[1].append(costly)
        self.state.select_card(costly)
        self.state.select_card(Card('missing', 1, 'Ruby', 0))
        self.assertIs(self.state.selected_card, self.card)

    def test_confirm_purchase_clears_selection_and_refills_slot(self):
        replacement = Card('replacement', 1, 'Onyx', 0)
        self.state.decks[1] = [replacement]
        self.state.select_card(self.card)
        self.state.buy_card(self.state.selected_card)
        self.assertIsNone(self.state.selected_card)
        self.assertEqual(self.state.selected_tokens, {})
        self.assertIs(self.state.players[0].cards[self.card.id], self.card)
        self.assertEqual(self.state.market[1], [replacement])

    def test_pass_and_take_clear_selection(self):
        self.state.select_card(self.card)
        self.state.pass_turn()
        self.assertIsNone(self.state.selected_card)
        self.state.select_token('Ruby')
        self.state.take_tokens(self.state.selected_tokens)
        self.assertEqual(self.state.selected_tokens, {})

    def test_finished_game_cannot_select(self):
        self.state.turn.finished = True
        self.state.select_card(self.card)
        self.state.select_token('Ruby')
        self.assertIsNone(self.state.selected_card)
        self.assertEqual(self.state.selected_tokens, {})
