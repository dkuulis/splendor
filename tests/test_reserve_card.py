import copy
import unittest

from game import Card, State
from game.constants import GEMS, GOLD, RUBY, MAX_RESERVATIONS, TOKEN_LIMIT


class ReserveCardTests(unittest.TestCase):
    def make_state(self):
        state = State()
        card = Card('reserve', 2, RUBY, 3, {RUBY: 7})
        state.market[2] = [card]
        state.select_card(card)
        state.select_token(GOLD)
        return state, card

    def test_reserve_transfers_card_and_gold_and_refills_same_slot(self):
        state, card = self.make_state()
        player = state.current_player
        player.tokens = {RUBY: 7, GOLD: 2}
        player.reserved_cards = [Card('old', 1, RUBY, 1, {})
                                 for _ in range(MAX_RESERVATIONS - 1)]
        replacement = Card('next', 2, RUBY, 1, {})
        state.decks[2] = [replacement]
        gold = state.supply[GOLD]
        state.turn.consecutive_passes = 1
        self.assertEqual(state.action_label, 'Reserve')
        self.assertIsNone(state.action_error)
        state.perform_action()
        self.assertIs(player.reserved_cards[-1], card)
        self.assertEqual(len(player.reserved_cards), MAX_RESERVATIONS)
        self.assertEqual(player.tokens, {RUBY: 7, GOLD: 3})
        self.assertEqual(state.supply[GOLD], gold - 1)
        self.assertEqual(player.points, 0)
        self.assertEqual(player.discounts, dict.fromkeys(GEMS, 0))
        self.assertEqual(state.market[2], [replacement])
        self.assertEqual(state.decks[2], [])
        self.assertEqual(state.players[1].reserved_cards, [])
        self.assertEqual(state.turn.active_player, 1)
        self.assertEqual(state.turn.consecutive_passes, 0)
        self.assertIsNone(state.selected_card)
        self.assertEqual(state.selected_tokens, {})
        self.assertIn('reserved by YOU', state.log[0])
        self.assertIn('Revealed:', state.log[1])

    def test_reserve_from_exhausted_deck_finishes_computer_turn(self):
        state, card = self.make_state()
        state.turn.active_player = 1
        state.turn.final_round = True
        state.reserve_card()
        self.assertEqual(state.market[2], [])
        self.assertEqual(state.players[1].reserved_cards, [card])
        self.assertEqual(state.players[1].tokens, {GOLD: 1})
        self.assertTrue(state.turn.finished)

    def test_invalid_reservations_do_not_change_state(self):
        for case in ('full tokens', 'full reservations', 'no gold supply',
                     'missing card', 'no selected gold', 'extra gem', 'finished'):
            with self.subTest(case=case):
                state, card = self.make_state()
                if case == 'full tokens':
                    state.current_player.tokens = {RUBY: TOKEN_LIMIT - 1, GOLD: 1}
                elif case == 'full reservations':
                    state.current_player.reserved_cards = [card] * MAX_RESERVATIONS
                elif case == 'no gold supply':
                    state.supply[GOLD] = 0
                elif case == 'missing card':
                    state.market[2].clear()
                elif case == 'no selected gold':
                    state.selected_tokens.clear()
                elif case == 'extra gem':
                    state.selected_tokens[RUBY] = 1
                else:
                    state.turn.finished = True
                before = copy.deepcopy((state.supply, state.current_player.tokens,
                                        vars(state.turn), state.log, state.selected_tokens))
                reserved = list(state.current_player.reserved_cards)
                market = list(state.market[2])
                self.assertIsNotNone(state.reserve_card_error())
                with self.assertRaises(ValueError):
                    state.reserve_card()
                self.assertEqual((state.supply, state.current_player.tokens,
                                  vars(state.turn), state.log, state.selected_tokens), before)
                self.assertEqual(state.current_player.reserved_cards, reserved)
                self.assertEqual(state.market[2], market)
                self.assertIs(state.selected_card, card)
