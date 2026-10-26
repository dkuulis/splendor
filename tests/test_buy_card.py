import copy
import unittest

from game import Card, State


class BuyCardTests(unittest.TestCase):
    def test_discount_payment_and_replacement(self):
        state = State()
        player = state.players[0]
        player.cards = {'owned': Card('owned', 1, 'Ruby', 0)}
        player.gems = {'Ruby': 2, 'Sapphire': 1}
        card = Card('buy', 2, 'Emerald', 2, {'Ruby': 3, 'Sapphire': 1})
        replacement = Card('next', 2, 'Diamond', 1)
        state.market[2] = [card]
        state.decks[2] = [replacement]
        self.assertTrue(state.can_buy(card))
        state.buy_card(card)
        self.assertEqual(player.gems, {})
        self.assertEqual(state.bank['Ruby'], 6)
        self.assertEqual(state.bank['Sapphire'], 5)
        self.assertIs(player.cards['buy'], card)
        self.assertEqual(player.points, 2)
        self.assertEqual(player.discounts, {'Ruby': 1, 'Emerald': 1})
        self.assertEqual(state.market[2], [replacement])
        self.assertEqual(state.decks[2], [])
        self.assertEqual(state.turn.active_player, 1)
        self.assertEqual(state.log, [
            "2-point Emerald card (level 2) bought by YOU for 1 Sapphire, 2 Ruby.",
            "Revealed: 1-point Diamond card (level 2), costing no gems.",
        ])

    def test_free_purchase_and_exhausted_deck(self):
        state = State()
        state.players[0].cards = {'owned': Card('owned', 1, 'Ruby', 0)}
        card = Card('free', 1, 'Onyx', 0, {'Ruby': 1})
        state.market[1] = [card]
        state.turn.consecutive_passes = 1
        state.buy_card(card)
        self.assertEqual(state.players[0].gems, {})
        self.assertEqual(state.market[1], [])
        self.assertEqual(state.turn.consecutive_passes, 0)
        self.assertEqual(state.turn.active_player, 1)
        self.assertEqual(state.log, ["0-point Onyx card (level 1) bought by YOU for no gems."])

    def test_rejected_purchase_is_atomic(self):
        state = State()
        card = Card('costly', 1, 'Ruby', 0, {'Ruby': 2})
        state.market[1] = [card]
        state.players[0].gems = {'Ruby': 1}
        before = copy.deepcopy((state.bank, state.players[0].gems, vars(state.turn), state.log))
        self.assertFalse(state.can_buy(card))
        with self.assertRaises(ValueError):
            state.buy_card(card)
        self.assertEqual((state.bank, state.players[0].gems, vars(state.turn), state.log), before)
        self.assertEqual(state.market[1], [card])
        self.assertEqual(state.players[0].cards, {})
        with self.assertRaises(ValueError):
            state.buy_card(Card('missing', 1, 'Ruby', 0))

    def test_card_cannot_discount_its_own_purchase(self):
        state = State()
        card = Card('self', 1, 'Ruby', 0, {'Ruby': 1})
        state.market[1] = [card]
        self.assertFalse(state.can_buy(card))

    def test_both_players_buy_and_finish_round(self):
        state = State()
        for i, player in enumerate(state.players):
            player.cards = {f'owned-{i}': Card(f'owned-{i}', 3, 'Ruby', 14)}
        first = Card('first', 3, 'Onyx', 1)
        second = Card('second', 3, 'Diamond', 2)
        state.market[3] = [first, second]
        state.buy_card(first)
        self.assertTrue(state.turn.final_round)
        self.assertIn("YOU reached 15 points and triggered the final round.", state.log)
        self.assertFalse(state.turn.finished)
        self.assertEqual(state.turn.active_player, 1)
        state.buy_card(second)
        self.assertTrue(state.turn.finished)
        self.assertEqual(state.turn.winner, 1)
        self.assertEqual(sum("triggered the final round" in message for message in state.log), 1)
        self.assertFalse(state.can_buy(first))
        with self.assertRaises(ValueError):
            state.buy_card(first)


if __name__ == '__main__':
    unittest.main()
