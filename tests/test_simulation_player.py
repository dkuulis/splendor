import unittest

from game.constants import EMERALD, GOLD, RUBY, TOKENS
from simulation import Card, Player


class SimulationPlayerTests(unittest.TestCase):
    def test_payment_combines_color_shortfalls_after_discounts(self):
        ruby = TOKENS.index(RUBY)
        emerald = TOKENS.index(EMERALD)
        gold = TOKENS.index(GOLD)
        cost = [0] * len(TOKENS)
        cost[ruby], cost[emerald] = 4, 2
        card = Card(0, emerald, 1, cost)
        for available_gold in (1, 2, 3):
            with self.subTest(gold=available_gold):
                player = Player(0)
                player.discounts[ruby] = 2
                player.tokens[ruby] = player.tokens[emerald] = 1
                player.tokens[gold] = available_gold
                before = player.tokens[:], player.discounts[:]
                payment = player.payment(card)
                if available_gold < 2:
                    self.assertIsNone(payment)
                else:
                    expected = [0] * len(TOKENS)
                    expected[ruby] = expected[emerald] = -1
                    expected[gold] = -2
                    self.assertEqual(payment, tuple(expected))
                self.assertEqual((player.tokens, player.discounts), before)

    def test_free_discounted_card_returns_zero_payment_not_none(self):
        ruby = TOKENS.index(RUBY)
        player = Player(1)
        player.discounts[ruby] = 3
        player.tokens[ruby] = 2
        cost = [0] * len(TOKENS)
        cost[ruby] = 2
        card = Card(0, ruby, 1, cost)
        self.assertEqual(player.payment(card), (0,) * len(TOKENS))
        self.assertEqual(player.tokens[ruby], 2)
