import copy
import unittest

from game.selection import Selection

from game.constants import GEMS, DIAMOND, SAPPHIRE, EMERALD, RUBY, ONYX, GOLD
from game import Card, State


class BuyCardTests(unittest.TestCase):
    def test_purchase_uses_supplied_card_instead_of_pending_card(self):
        state = State()
        selection = Selection()
        selected = Card('selected', 1, RUBY, 0, {})
        purchased = Card('purchased', 1, ONYX, 1, {})
        state.market[1] = [selected, purchased]
        selection.select_card(selected, state)
        state.buy_card(purchased)
        self.assertEqual(state.players[0].cards[ONYX], [purchased])
        self.assertEqual(state.players[0].cards[RUBY], [])
        self.assertEqual(state.market[1], [selected])
        self.assertIs(selection.card, selected)

    def test_gold_covers_shortfalls_after_discounts_and_returns_actual_payment(self):
        state = State()
        selection = Selection()
        player = state.current_player
        player.add_card(Card('discount', 1, RUBY, 0, {}))
        player.tokens = {RUBY: 1, GOLD: 3, ONYX: 1}
        card = Card('wild', 2, EMERALD, 2, {RUBY: 3, SAPPHIRE: 2})
        state.market[2] = [card]
        supply = dict(state.supply)
        self.assertTrue(state.can_buy(card))
        self.assertEqual(state.current_player.card_payment(card), {RUBY: 1, GOLD: 3})
        self.assertEqual(player.tokens, {RUBY: 1, GOLD: 3, ONYX: 1})
        selection.select_card(card, state)
        self.assertTrue(selection.can_perform_action(state))
        selection.perform_action(state)
        self.assertEqual(player.tokens, {ONYX: 1})
        supply[RUBY] += 1
        supply[GOLD] += 3
        self.assertEqual(state.supply, supply)
        self.assertEqual(player.cards[EMERALD], [card])

    def test_matching_gems_and_free_cards_preserve_gold(self):
        for price in (0, 2):
            with self.subTest(price=price):
                state = State()
                selection = Selection()
                player = state.current_player
                player.tokens = {RUBY: 3, GOLD: 2}
                card = Card('matching', 1, EMERALD, 0, {RUBY: price})
                state.market[1] = [card]
                selection.select_card(card, state)
                state.buy_card(card)
                self.assertEqual(player.tokens, {RUBY: 3 - price, GOLD: 2})

    def test_gold_cannot_be_reused_for_multiple_missing_colors(self):
        state = State()
        selection = Selection()
        card = Card('short', 1, EMERALD, 0, {RUBY: 1, SAPPHIRE: 1})
        state.market[1] = [card]
        player = state.current_player
        player.tokens = {GOLD: 1}
        selection.select_card(card, state)
        supply = dict(state.supply)
        self.assertFalse(state.can_buy(card))
        self.assertFalse(selection.can_buy_card(state))
        self.assertEqual(player.tokens, {GOLD: 1})
        self.assertEqual(state.supply, supply)
        self.assertEqual(state.market[1], [card])
        self.assertEqual(state.turn.active_player, 0)

    def test_purchase_appends_to_color_and_preserves_other_holdings(self):
        state = State()
        selection = Selection()
        player = state.current_player
        owned = player.add_card(Card('owned', 1, RUBY, 1, {}))
        other = player.add_card(Card('other', 1, ONYX, 2, {}))
        card = Card('buy', 2, RUBY, 3, {RUBY: 1})
        state.market[2] = [card]
        selection.select_card(card, state)
        state.buy_card(card)
        self.assertEqual(player.cards[RUBY], [owned, card])
        self.assertEqual(player.cards[ONYX], [other])
        self.assertEqual(player.points, 6)
        self.assertEqual(player.discounts, {**dict.fromkeys(GEMS, 0), RUBY: 2, ONYX: 1})
        for cards in state.players[1].cards.values():
            self.assertEqual(cards, [])

    def test_discount_payment_and_replacement(self):
        state = State()
        selection = Selection()
        player = state.players[0]
        player.add_card(Card('owned', 1, RUBY, 0, {}))
        player.tokens = {RUBY: 2, SAPPHIRE: 1}
        card = Card('buy', 2, EMERALD, 2, {RUBY: 3, SAPPHIRE: 1})
        replacement = Card('next', 2, DIAMOND, 1, {})
        state.market[2] = [card]
        state.decks[2] = [replacement]
        self.assertTrue(state.can_buy(card))
        selection.card = card
        state.buy_card(card)
        self.assertEqual(player.tokens, {})
        self.assertEqual(state.supply[RUBY], 6)
        self.assertEqual(state.supply[SAPPHIRE], 5)
        self.assertEqual(player.cards[EMERALD], [card])
        self.assertEqual(player.points, 2)
        self.assertEqual(player.discounts, {**dict.fromkeys(GEMS, 0), RUBY: 1, EMERALD: 1})
        self.assertEqual(state.market[2], [replacement])
        self.assertEqual(state.decks[2], [])
        self.assertEqual(state.turn.active_player, 1)

    def test_free_purchase_and_exhausted_deck(self):
        state = State()
        selection = Selection()
        state.players[0].add_card(Card('owned', 1, RUBY, 0, {}))
        card = Card('free', 1, ONYX, 0, {RUBY: 1})
        state.market[1] = [card]
        state.turn.consecutive_passes = 1
        selection.card = card
        state.buy_card(card)
        self.assertEqual(state.players[0].tokens, {})
        self.assertEqual(state.market[1], [])
        self.assertEqual(state.turn.consecutive_passes, 0)
        self.assertEqual(state.turn.active_player, 1)

    def test_purchase_permissions_do_not_change_state(self):
        state = State()
        selection = Selection()
        card = Card('costly', 1, RUBY, 0, {RUBY: 2})
        state.market[1] = [card]
        state.players[0].tokens = {RUBY: 1}
        before = copy.deepcopy((state.supply, state.players[0].tokens, vars(state.turn)))
        self.assertFalse(state.can_buy(card))
        selection.card = card
        self.assertFalse(selection.can_buy_card(state))
        self.assertEqual((state.supply, state.players[0].tokens, vars(state.turn)), before)
        self.assertEqual(state.market[1], [card])
        for cards in state.players[0].cards.values():
            self.assertEqual(cards, [])
        selection.card = Card('missing', 1, RUBY, 0, {})
        self.assertFalse(selection.can_buy_card(state))

    def test_card_cannot_discount_its_own_purchase(self):
        state = State()
        card = Card('self', 1, RUBY, 0, {RUBY: 1})
        state.market[1] = [card]
        self.assertFalse(state.can_buy(card))

    def test_both_players_buy_and_finish_round(self):
        state = State()
        selection = Selection()
        for i, player in enumerate(state.players):
            player.add_card(Card(f'owned-{i}', 3, RUBY, 14, {}))
        first = Card('first', 3, ONYX, 1, {})
        second = Card('second', 3, DIAMOND, 2, {})
        state.market[3] = [first, second]
        selection.card = first
        state.buy_card(first)
        self.assertTrue(state.turn.final_round)
        self.assertFalse(state.turn.finished)
        self.assertEqual(state.turn.active_player, 1)
        selection.card = second
        state.buy_card(second)
        self.assertTrue(state.turn.finished)
        self.assertEqual(state.turn.winner, 1)
        self.assertFalse(state.can_buy(first))
        selection.card = first
        self.assertFalse(selection.can_buy_card(state))


if __name__ == '__main__':
    unittest.main()
