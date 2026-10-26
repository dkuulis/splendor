import unittest

from game import Card, State
from game.constants import GEMS, GOLD, RUBY, SAPPHIRE


class BuyReservedCardTests(unittest.TestCase):
    def setUp(self):
        self.state = State()
        self.card = Card('reserved', 2, SAPPHIRE, 3, {RUBY: 3})
        self.state.current_player.reserved_cards.append(self.card)

    def test_reserved_card_selects_toggles_and_rejects_gold(self):
        state = self.state
        state.select_card(self.card)
        self.assertIs(state.selected_card, self.card)
        self.assertEqual(state.action_label, 'Buy')
        self.assertIsNotNone(state.action_error)
        state.select_token(GOLD)
        self.assertIs(state.selected_card, self.card)
        self.assertEqual(state.selected_tokens, {})
        self.assertEqual(state.action_label, 'Buy')
        state.select_card(self.card)
        self.assertIsNone(state.selected_card)

    def test_reserved_purchase_uses_discounts_and_gold_without_touching_market(self):
        state = self.state
        player = state.current_player
        player.add_card(Card('bonus', 1, RUBY, 0, {}))
        player.tokens = {RUBY: 1, GOLD: 1}
        market = Card('market', 2, RUBY, 1, {})
        deck = Card('deck', 2, RUBY, 2, {})
        state.market[2] = [market]
        state.decks[2] = [deck]
        self.assertTrue(state.can_buy(self.card))
        state.select_card(self.card)
        state.perform_action()
        self.assertEqual(player.reserved_cards, [])
        self.assertEqual(player.cards[SAPPHIRE], [self.card])
        self.assertEqual(player.tokens, {})
        self.assertEqual(player.points, 3)
        self.assertEqual(player.discounts, {**dict.fromkeys(GEMS, 0), RUBY: 1, SAPPHIRE: 1})
        self.assertEqual(state.market[2], [market])
        self.assertEqual(state.decks[2], [deck])
        self.assertEqual(len(state.log), 1)
        self.assertEqual(state.turn.active_player, 1)
        self.assertIsNone(state.selected_card)

    def test_unaffordable_reserved_purchase_and_rereservation_are_rejected(self):
        state = self.state
        state.select_card(self.card)
        with self.assertRaises(ValueError):
            state.buy_card()
        state.selected_tokens = {GOLD: 1}
        gold = state.supply[GOLD]
        with self.assertRaisesRegex(ValueError, 'already reserved'):
            state.reserve_card()
        self.assertEqual(state.current_player.reserved_cards, [self.card])
        self.assertEqual(state.current_player.tokens, {})
        self.assertEqual(state.supply[GOLD], gold)
        self.assertEqual(state.turn.active_player, 0)
        self.assertEqual(state.log, [])

    def test_opponents_or_removed_reserved_card_cannot_be_selected_or_bought(self):
        state = self.state
        state.current_player.reserved_cards.clear()
        state.players[1].reserved_cards.append(self.card)
        state.current_player.tokens = {GOLD: 5}
        state.select_card(self.card)
        self.assertIsNone(state.selected_card)
        self.assertFalse(state.can_buy(self.card))
        state.selected_card = self.card
        with self.assertRaises(ValueError):
            state.buy_card()
        self.assertEqual(state.players[1].reserved_cards, [self.card])
        state.players[1].reserved_cards.clear()
        self.assertFalse(state.can_buy(self.card))
