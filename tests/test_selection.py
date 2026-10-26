import copy
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
        for cards in state.players[0].cards.values():
            self.assertEqual(cards, [])
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
        self.state.current_player.tokens = {'Ruby': 10}
        self.assertEqual(self.state.action_label, 'Pass')
        self.assertIsNone(self.state.action_error)
        self.state.perform_action()
        self.assertEqual(self.state.log, ['YOU passed.'])
        self.assertEqual(self.state.turn.active_player, 1)

    def test_selected_gems_are_taken_in_one_turn(self):
        self.state.select_token('Ruby')
        self.state.select_token('Diamond')
        self.assertEqual(self.state.action_label, 'Take')
        self.assertIsNone(self.state.action_error)
        self.state.perform_action()
        self.assertEqual(self.state.players[0].tokens, {'Ruby': 1, 'Diamond': 1})
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
                card = Card('selected', 1, 'Ruby', 1)
                state.market[1] = [card]
                if case in ('missing card', 'unaffordable card', 'finished buy'):
                    state.select_card(card)
                    if case == 'missing card':
                        state.market[1].clear()
                    elif case == 'unaffordable card':
                        card.cost = {'Ruby': 1}
                elif case != 'finished pass':
                    state.select_token('Ruby')
                    if case == 'unavailable gem':
                        state.supply['Ruby'] = 0
                    elif case == 'full inventory':
                        state.current_player.tokens = {'Diamond': 10}
                    elif case == 'too many gems':
                        for token in ('Diamond', 'Onyx', 'Emerald'):
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
        self.state.select_token('Ruby')
        self.state.take_tokens()
        self.assertEqual(self.state.selected_tokens, {})

    def test_finished_game_cannot_select(self):
        self.state.turn.finished = True
        self.state.select_card(self.card)
        self.state.select_token('Ruby')
        self.assertIsNone(self.state.selected_card)
        self.assertEqual(self.state.selected_tokens, {})
