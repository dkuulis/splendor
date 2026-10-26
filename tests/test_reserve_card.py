import copy
import unittest

from game.selection import Selection

from game import Card, State
from game.constants import GEMS, GOLD, RUBY, MAX_RESERVATIONS


class ReserveCardTests(unittest.TestCase):
    def make_state(self):
        state = State()
        selection = Selection()
        card = Card('reserve', 2, RUBY, 3, {RUBY: 7})
        state.market[2] = [card]
        selection.reserve_card(card, state)
        return state, selection, card

    def test_reservation_uses_supplied_card_instead_of_pending_card(self):
        state, selection, selected = self.make_state()
        reserved = Card('other', 2, RUBY, 0, {})
        state.market[2].append(reserved)
        state.reserve_card(reserved)
        self.assertEqual(state.players[0].reserved_cards, [reserved])
        self.assertEqual(state.players[0].tokens, {GOLD: 1})
        self.assertEqual(state.market[2], [selected])
        self.assertIs(selection.card, selected)

    def test_reserve_transfers_card_and_gold_and_refills_same_slot(self):
        state, selection, card = self.make_state()
        player = state.current_player
        player.tokens = {RUBY: 7, GOLD: 2}
        player.reserved_cards = [Card('old', 1, RUBY, 1, {})
                                 for _ in range(MAX_RESERVATIONS - 1)]
        replacement = Card('next', 2, RUBY, 1, {})
        state.decks[2] = [replacement]
        gold = state.supply[GOLD]
        state.turn.consecutive_passes = 1
        self.assertEqual(selection.action_kind.capitalize(), 'Reserve')
        self.assertTrue(selection.can_perform_action(state))
        selection.perform_action(state)
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
        self.assertIsNone(selection.card)
        self.assertEqual(selection.tokens, {})

    def test_reserve_from_exhausted_deck_finishes_computer_turn(self):
        state, selection, card = self.make_state()
        state.turn.active_player = 1
        state.turn.final_round = True
        state.reserve_card(card)
        self.assertEqual(state.market[2], [])
        self.assertEqual(state.players[1].reserved_cards, [card])
        self.assertEqual(state.players[1].tokens, {GOLD: 1})
        self.assertTrue(state.turn.finished)

    def test_reservation_permissions_do_not_change_state(self):
        for case in ('full reservations', 'no gold supply',
                     'missing card', 'no selected gold', 'extra gem', 'finished'):
            with self.subTest(case=case):
                state, selection, card = self.make_state()
                if case == 'full reservations':
                    state.current_player.reserved_cards = [card] * MAX_RESERVATIONS
                elif case == 'no gold supply':
                    state.supply[GOLD] = 0
                elif case == 'missing card':
                    state.market[2].clear()
                elif case == 'no selected gold':
                    selection.tokens.clear()
                elif case == 'extra gem':
                    selection.tokens[RUBY] = 1
                else:
                    state.turn.finished = True
                before = copy.deepcopy((state.supply, state.current_player.tokens,
                                        vars(state.turn), selection.tokens))
                reserved = list(state.current_player.reserved_cards)
                market = list(state.market[2])
                self.assertFalse(selection.can_reserve_card(state))
                self.assertFalse(selection.can_perform_action(state))
                self.assertEqual((state.supply, state.current_player.tokens,
                                  vars(state.turn), selection.tokens), before)
                self.assertEqual(state.current_player.reserved_cards, reserved)
                self.assertEqual(state.market[2], market)
                self.assertIs(selection.card, card)
