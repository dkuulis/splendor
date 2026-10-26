import unittest

from ai.greedy import GreedyAI
from game import Card, State


class GreedyAITests(unittest.TestCase):
    def setUp(self):
        self.state = State()
        self.player = self.state.current_player

    def test_buys_highest_points_before_cheapest(self):
        cheap = Card("cheap", 1, "Ruby", 1)
        valuable = Card("valuable", 2, "Emerald", 3, {"Diamond": 2})
        self.state.market[1] = [cheap]
        self.state.market[2] = [valuable]
        self.player.gems = {"Diamond": 2}
        GreedyAI().play_turn(self.state)
        self.assertEqual(self.player.cards, {"valuable": valuable})
        self.assertEqual(self.player.gems, {})
        self.assertEqual(self.state.turn.active_player, 1)

    def test_equal_points_use_discounted_payment(self):
        owned = Card("owned", 1, "Ruby", 0)
        self.player.cards[owned.id] = owned
        expensive = Card("expensive", 1, "Emerald", 1, {"Diamond": 2})
        discounted = Card("discounted", 1, "Onyx", 1, {"Ruby": 2})
        self.state.market[1] = [expensive, discounted]
        self.player.gems = {"Diamond": 2, "Ruby": 1}
        GreedyAI().play_turn(self.state)
        self.assertIn("discounted", self.player.cards)
        self.assertEqual(self.player.gems, {"Diamond": 2})

    def test_closest_card_accounts_for_owned_gems_and_discounts(self):
        self.player.cards["owned"] = Card("owned", 1, "Ruby", 0)
        self.player.gems = {"Ruby": 2}
        self.state.market[1] = [
            Card("far", 1, "Onyx", 0, {"Diamond": 2}),
            Card("near", 1, "Emerald", 0, {"Ruby": 4}),
        ]
        GreedyAI().play_turn(self.state)
        self.assertEqual(self.player.gems, {"Ruby": 3})

    def test_takes_three_scarcest_needed_colors(self):
        self.state.market[1] = [Card("target", 1, "Onyx", 1,
                                     {"Diamond": 1, "Sapphire": 1, "Emerald": 1, "Ruby": 1})]
        self.state.bank.update(Diamond=4, Sapphire=3, Emerald=1, Ruby=2)
        GreedyAI().play_turn(self.state)
        self.assertEqual(self.player.gems, {"Emerald": 1, "Ruby": 1, "Sapphire": 1})
        self.assertEqual(self.state.log, ["YOU took 1 Emerald, 1 Ruby, 1 Sapphire."])

    def test_capacity_limits_collection_to_scarcest_color(self):
        self.player.gems = {"Onyx": 9}
        self.state.market[1] = [Card("target", 1, "Emerald", 0, {"Diamond": 1, "Ruby": 1})]
        self.state.bank["Ruby"] = 1
        GreedyAI().play_turn(self.state)
        self.assertEqual(self.player.gems, {"Onyx": 9, "Ruby": 1})

    def test_skips_blocked_target_and_takes_only_one_of_each_color(self):
        self.state.bank["Diamond"] = 0
        self.state.market[1] = [
            Card("blocked", 1, "Onyx", 0, {"Diamond": 1}),
            Card("available", 1, "Emerald", 0, {"Ruby": 2}),
        ]
        GreedyAI().play_turn(self.state)
        self.assertEqual(self.player.gems, {"Ruby": 1})

    def test_passes_when_no_useful_collection_is_possible(self):
        for situation in ("empty market", "empty bank", "full inventory"):
            with self.subTest(situation=situation):
                state = State()
                if situation != "empty market":
                    state.market[1] = [Card("target", 1, "Emerald", 0, {"Ruby": 1})]
                if situation == "empty bank":
                    state.bank = {}
                if situation == "full inventory":
                    state.current_player.gems = {"Diamond": 10}
                GreedyAI().play_turn(state)
                self.assertEqual(state.log, ["YOU passed."])
                self.assertEqual(state.turn.active_player, 1)


if __name__ == '__main__':
    unittest.main()
