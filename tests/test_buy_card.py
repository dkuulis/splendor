import copy
import unittest

from game.constants import DIAMOND, SAPPHIRE, EMERALD, RUBY, ONYX, GOLD
from game import Card, State


class BuyCardTests(unittest.TestCase):
    def test_gold_covers_shortfalls_after_discounts_and_returns_actual_payment(self):
        state = State()
        player = state.current_player
        player.add_card(Card('discount', 1, RUBY, 0, {}))
        player.tokens = {RUBY: 1, GOLD: 3, ONYX: 1}
        card = Card('wild', 2, EMERALD, 2, {RUBY: 3, SAPPHIRE: 2})
        state.market[2] = [card]
        supply = dict(state.supply)
        self.assertTrue(state.can_buy(card))
        self.assertEqual(state.card_payment(card), {RUBY: 1, GOLD: 3})
        self.assertEqual(player.tokens, {RUBY: 1, GOLD: 3, ONYX: 1})
        state.select_card(card)
        self.assertIsNone(state.action_error)
        state.perform_action()
        self.assertEqual(player.tokens, {ONYX: 1})
        supply[RUBY] += 1
        supply[GOLD] += 3
        self.assertEqual(state.supply, supply)
        self.assertEqual(player.cards[EMERALD], [card])
        self.assertIn('for 3 Gold, 1 Ruby.', state.log[0])

    def test_matching_gems_and_free_cards_preserve_gold(self):
        for price in (0, 2):
            with self.subTest(price=price):
                state = State()
                player = state.current_player
                player.tokens = {RUBY: 3, GOLD: 2}
                card = Card('matching', 1, EMERALD, 0, {RUBY: price})
                state.market[1] = [card]
                state.select_card(card)
                state.buy_card()
                self.assertEqual(player.tokens, {RUBY: 3 - price, GOLD: 2})

    def test_gold_cannot_be_reused_for_multiple_missing_colors(self):
        state = State()
        card = Card('short', 1, EMERALD, 0, {RUBY: 1, SAPPHIRE: 1})
        state.market[1] = [card]
        player = state.current_player
        player.tokens = {GOLD: 1}
        state.select_card(card)
        supply = dict(state.supply)
        self.assertFalse(state.can_buy(card))
        with self.assertRaises(ValueError):
            state.buy_card()
        self.assertEqual(player.tokens, {GOLD: 1})
        self.assertEqual(state.supply, supply)
        self.assertEqual(state.market[1], [card])
        self.assertEqual(state.turn.active_player, 0)
        self.assertEqual(state.log, [])

    def test_purchase_appends_to_color_and_preserves_other_holdings(self):
        state = State()
        player = state.current_player
        owned = player.add_card(Card('owned', 1, RUBY, 1, {}))
        other = player.add_card(Card('other', 1, ONYX, 2, {}))
        card = Card('buy', 2, RUBY, 3, {RUBY: 1})
        state.market[2] = [card]
        state.select_card(card)
        state.buy_card()
        self.assertEqual(player.cards[RUBY], [owned, card])
        self.assertEqual(player.cards[ONYX], [other])
        self.assertEqual(player.points, 6)
        self.assertEqual(player.discounts, {RUBY: 2, ONYX: 1})
        for cards in state.players[1].cards.values():
            self.assertEqual(cards, [])

    def test_discount_payment_and_replacement(self):
        state = State()
        player = state.players[0]
        player.add_card(Card('owned', 1, RUBY, 0, {}))
        player.tokens = {RUBY: 2, SAPPHIRE: 1}
        card = Card('buy', 2, EMERALD, 2, {RUBY: 3, SAPPHIRE: 1})
        replacement = Card('next', 2, DIAMOND, 1, {})
        state.market[2] = [card]
        state.decks[2] = [replacement]
        self.assertTrue(state.can_buy(card))
        state.selected_card = card
        state.buy_card()
        self.assertEqual(player.tokens, {})
        self.assertEqual(state.supply[RUBY], 6)
        self.assertEqual(state.supply[SAPPHIRE], 5)
        self.assertEqual(player.cards[EMERALD], [card])
        self.assertEqual(player.points, 2)
        self.assertEqual(player.discounts, {RUBY: 1, EMERALD: 1})
        self.assertEqual(state.market[2], [replacement])
        self.assertEqual(state.decks[2], [])
        self.assertEqual(state.turn.active_player, 1)
        self.assertEqual(state.log, [
            "2-point Emerald card (level 2) bought by YOU for 1 Sapphire, 2 Ruby.",
            "Revealed: 1-point Diamond card (level 2), costing no gems.",
        ])

    def test_free_purchase_and_exhausted_deck(self):
        state = State()
        state.players[0].add_card(Card('owned', 1, RUBY, 0, {}))
        card = Card('free', 1, ONYX, 0, {RUBY: 1})
        state.market[1] = [card]
        state.turn.consecutive_passes = 1
        state.selected_card = card
        state.buy_card()
        self.assertEqual(state.players[0].tokens, {})
        self.assertEqual(state.market[1], [])
        self.assertEqual(state.turn.consecutive_passes, 0)
        self.assertEqual(state.turn.active_player, 1)
        self.assertEqual(state.log, ["0-point Onyx card (level 1) bought by YOU for no gems."])

    def test_rejected_purchase_is_atomic(self):
        state = State()
        card = Card('costly', 1, RUBY, 0, {RUBY: 2})
        state.market[1] = [card]
        state.players[0].tokens = {RUBY: 1}
        before = copy.deepcopy((state.supply, state.players[0].tokens, vars(state.turn), state.log))
        self.assertFalse(state.can_buy(card))
        with self.assertRaises(ValueError):
            state.selected_card = card
            state.buy_card()
        self.assertEqual((state.supply, state.players[0].tokens, vars(state.turn), state.log), before)
        self.assertEqual(state.market[1], [card])
        for cards in state.players[0].cards.values():
            self.assertEqual(cards, [])
        with self.assertRaises(ValueError):
            state.selected_card = Card('missing', 1, RUBY, 0, {})
            state.buy_card()

    def test_card_cannot_discount_its_own_purchase(self):
        state = State()
        card = Card('self', 1, RUBY, 0, {RUBY: 1})
        state.market[1] = [card]
        self.assertFalse(state.can_buy(card))

    def test_both_players_buy_and_finish_round(self):
        state = State()
        for i, player in enumerate(state.players):
            player.add_card(Card(f'owned-{i}', 3, RUBY, 14, {}))
        first = Card('first', 3, ONYX, 1, {})
        second = Card('second', 3, DIAMOND, 2, {})
        state.market[3] = [first, second]
        state.selected_card = first
        state.buy_card()
        self.assertTrue(state.turn.final_round)
        self.assertIn("YOU reached 15 points and triggered the final round.", state.log)
        self.assertFalse(state.turn.finished)
        self.assertEqual(state.turn.active_player, 1)
        state.selected_card = second
        state.buy_card()
        self.assertTrue(state.turn.finished)
        self.assertEqual(state.turn.winner, 1)
        self.assertEqual(sum("triggered the final round" in message for message in state.log), 1)
        self.assertFalse(state.can_buy(first))
        with self.assertRaises(ValueError):
            state.selected_card = first
            state.buy_card()


if __name__ == '__main__':
    unittest.main()
