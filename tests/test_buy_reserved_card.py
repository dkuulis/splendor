import unittest

from game.selection import Selection

from game import Card, State
from game.constants import GEMS, GOLD, RUBY, SAPPHIRE


class BuyReservedCardTests(unittest.TestCase):
    def setUp(self):
        self.state = State()
        self.selection = Selection()
        self.card = Card('reserved', 2, SAPPHIRE, 3, {RUBY: 3})
        self.state.current_player.reserved_cards.append(self.card)

    def test_reserved_card_selects_toggles_and_rejects_gold(self):
        state = self.state
        selection = self.selection
        state.current_player.tokens = {RUBY: 3}
        selection.select_card(self.card, state)
        self.assertIs(selection.card, self.card)
        self.assertEqual(selection.action_kind.capitalize(), 'Buy')
        self.assertTrue(selection.can_perform_action(state))
        selection.select_token(GOLD, state)
        self.assertIs(selection.card, self.card)
        self.assertEqual(selection.tokens, {})
        self.assertEqual(selection.action_kind.capitalize(), 'Buy')
        selection.select_card(self.card, state)
        self.assertIsNone(selection.card)

    def test_reserved_purchase_uses_discounts_and_gold_without_touching_market(self):
        state = self.state
        selection = self.selection
        player = state.current_player
        player.add_card(Card('bonus', 1, RUBY, 0, {}))
        player.tokens = {RUBY: 1, GOLD: 1}
        market = Card('market', 2, RUBY, 1, {})
        deck = Card('deck', 2, RUBY, 2, {})
        state.market[2] = [market]
        state.decks[2] = [deck]
        self.assertTrue(state.can_buy(self.card))
        selection.select_card(self.card, state)
        selection.perform_action(state)
        self.assertEqual(player.reserved_cards, [])
        self.assertEqual(player.cards[SAPPHIRE], [self.card])
        self.assertEqual(player.tokens, {})
        self.assertEqual(player.points, 3)
        self.assertEqual(player.discounts, {**dict.fromkeys(GEMS, 0), RUBY: 1, SAPPHIRE: 1})
        self.assertEqual(state.market[2], [market])
        self.assertEqual(state.decks[2], [deck])
        self.assertEqual(state.turn.active_player, 1)
        self.assertIsNone(selection.card)

    def test_unaffordable_reserved_purchase_and_rereservation_are_disallowed(self):
        state = self.state
        selection = self.selection
        selection.select_card(self.card, state)
        self.assertIsNone(selection.card)
        self.assertEqual(selection.action_kind, 'pass')
        # Permission checks also cover selections supplied directly.
        selection.card = self.card
        self.assertFalse(selection.can_buy_card(state))
        selection.tokens = {GOLD: 1}
        gold = state.supply[GOLD]
        self.assertFalse(selection.can_reserve_card(state))
        self.assertEqual(state.current_player.reserved_cards, [self.card])
        self.assertEqual(state.current_player.tokens, {})
        self.assertEqual(state.supply[GOLD], gold)
        self.assertEqual(state.turn.active_player, 0)

    def test_opponents_or_removed_reserved_card_cannot_be_selected_or_bought(self):
        state = self.state
        selection = self.selection
        state.current_player.reserved_cards.clear()
        state.players[1].reserved_cards.append(self.card)
        state.current_player.tokens = {GOLD: 5}
        selection.select_card(self.card, state)
        self.assertIsNone(selection.card)
        self.assertFalse(state.can_buy(self.card))
        selection.card = self.card
        self.assertFalse(selection.can_buy_card(state))
        self.assertEqual(state.players[1].reserved_cards, [self.card])
        state.players[1].reserved_cards.clear()
        self.assertFalse(state.can_buy(self.card))
