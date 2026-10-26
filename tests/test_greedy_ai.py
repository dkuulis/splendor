import unittest

from ai.greedy import GreedyAI
from game import Card, State


class GreedyAITests(unittest.TestCase):
    def setUp(self):
        self.state = State()
        self.player = self.state.current_player

    def test_replaces_pending_selection_before_collecting(self):
        self.state.market[1] = [Card('target', 1, 'Emerald', 0, {'Ruby': 1})]
        self.state.select_token('Diamond')
        GreedyAI().play_turn(self.state)
        self.assertEqual(self.player.tokens, {'Ruby': 1})
        self.assertEqual(self.state.selected_tokens, {})
        self.assertIsNone(self.state.selected_card)

    def test_buys_an_already_selected_card_without_toggling_it_off(self):
        card = Card('free', 1, 'Ruby', 1)
        self.state.market[1] = [card]
        self.state.select_card(card)
        GreedyAI().play_turn(self.state)
        self.assertEqual(self.player.cards, {'free': card})
        self.assertIsNone(self.state.selected_card)
        self.assertEqual(self.state.turn.active_player, 1)

    def test_buys_highest_points_before_cheapest(self):
        cheap = Card("cheap", 1, "Ruby", 1)
        valuable = Card("valuable", 2, "Emerald", 3, {"Diamond": 2})
        self.state.market[1] = [cheap]
        self.state.market[2] = [valuable]
        self.player.tokens = {"Diamond": 2}
        GreedyAI().play_turn(self.state)
        self.assertEqual(self.player.cards, {"valuable": valuable})
        self.assertEqual(self.player.tokens, {})
        self.assertEqual(self.state.turn.active_player, 1)

    def test_equal_points_use_discounted_payment(self):
        owned = Card("owned", 1, "Ruby", 0)
        self.player.cards[owned.id] = owned
        expensive = Card("expensive", 1, "Emerald", 1, {"Diamond": 2})
        discounted = Card("discounted", 1, "Onyx", 1, {"Ruby": 2})
        self.state.market[1] = [expensive, discounted]
        self.player.tokens = {"Diamond": 2, "Ruby": 1}
        GreedyAI().play_turn(self.state)
        self.assertIn("discounted", self.player.cards)
        self.assertEqual(self.player.tokens, {"Diamond": 2})

    def test_closest_card_accounts_for_owned_tokens_and_discounts(self):
        self.player.cards["owned"] = Card("owned", 1, "Ruby", 0)
        self.player.tokens = {"Ruby": 2}
        self.state.market[1] = [
            Card("far", 1, "Onyx", 0, {"Diamond": 2}),
            Card("near", 1, "Emerald", 0, {"Ruby": 4}),
        ]
        GreedyAI().play_turn(self.state)
        self.assertEqual(self.player.tokens, {"Ruby": 3, "Diamond": 1})
        self.assertEqual(self.state.log, ["YOU took Diamond, Ruby."])

    def test_prefers_fewer_collection_turns_over_fewer_tokens(self):
        self.state.market[1] = [
            Card("slow", 1, "Onyx", 0, {"Ruby": 3}),
            Card("quick", 1, "Emerald", 0, {"Diamond": 2, "Sapphire": 1, "Emerald": 1}),
        ]
        GreedyAI().play_turn(self.state)
        self.assertEqual(self.player.tokens, {"Diamond": 1, "Sapphire": 1, "Emerald": 1})

    def test_turn_estimate_accounts_for_three_token_limit(self):
        self.state.market[1] = [
            Card("two turns", 1, "Onyx", 0,
                 {"Diamond": 1, "Sapphire": 1, "Emerald": 1, "Ruby": 1}),
            Card("one turn", 1, "Emerald", 0, {"Onyx": 1, "Ruby": 1}),
        ]
        GreedyAI().play_turn(self.state)
        self.assertEqual(self.state.log, ["YOU took Diamond, Ruby, Onyx."])

    def test_spare_picks_skip_duplicate_token_types_and_use_next_targets(self):
        self.state.market[1] = [
            Card("first", 1, "Onyx", 0, {"Ruby": 1}),
            Card("second", 1, "Emerald", 0, {"Ruby": 1, "Sapphire": 1}),
            Card("third", 1, "Diamond", 0, {"Emerald": 2, "Onyx": 1}),
        ]
        self.state.supply["Onyx"] = 1
        GreedyAI().play_turn(self.state)
        self.assertEqual(self.player.tokens, {"Ruby": 1, "Sapphire": 1, "Onyx": 1})

    def test_spare_picks_respect_inventory_capacity(self):
        self.player.tokens = {"Onyx": 8}
        self.state.market[1] = [
            Card("first", 1, "Onyx", 0, {"Ruby": 1}),
            Card("second", 1, "Emerald", 0, {"Sapphire": 1, "Diamond": 1}),
        ]
        self.state.supply["Sapphire"] = 1
        GreedyAI().play_turn(self.state)
        self.assertEqual(self.player.tokens, {"Onyx": 8, "Ruby": 1, "Sapphire": 1})

    def test_takes_three_scarcest_needed_token_types(self):
        self.state.market[1] = [Card("target", 1, "Onyx", 1,
                                     {"Diamond": 1, "Sapphire": 1, "Emerald": 1, "Ruby": 1})]
        self.state.supply.update(Diamond=4, Sapphire=3, Emerald=1, Ruby=2)
        GreedyAI().play_turn(self.state)
        self.assertEqual(self.player.tokens, {"Emerald": 1, "Ruby": 1, "Sapphire": 1})
        self.assertEqual(self.state.log, ["YOU took Sapphire, Emerald, Ruby."])

    def test_capacity_limits_collection_to_scarcest_token_type(self):
        self.player.tokens = {"Onyx": 9}
        self.state.market[1] = [Card("target", 1, "Emerald", 0, {"Diamond": 1, "Ruby": 1})]
        self.state.supply["Ruby"] = 1
        GreedyAI().play_turn(self.state)
        self.assertEqual(self.player.tokens, {"Onyx": 9, "Ruby": 1})

    def test_skips_blocked_target_and_takes_only_one_of_each_token_type(self):
        self.state.supply["Diamond"] = 0
        self.state.market[1] = [
            Card("blocked", 1, "Onyx", 0, {"Diamond": 1}),
            Card("available", 1, "Emerald", 0, {"Ruby": 2}),
        ]
        GreedyAI().play_turn(self.state)
        self.assertEqual(self.player.tokens, {"Ruby": 1})

    def test_passes_when_no_useful_collection_is_possible(self):
        for situation in ("empty market", "empty bank", "full inventory"):
            with self.subTest(situation=situation):
                state = State()
                if situation != "empty market":
                    state.market[1] = [Card("target", 1, "Emerald", 0, {"Ruby": 1})]
                if situation == "empty bank":
                    state.supply = {}
                if situation == "full inventory":
                    state.current_player.tokens = {"Diamond": 10}
                GreedyAI().play_turn(state)
                self.assertEqual(state.log, ["YOU passed."])
                self.assertEqual(state.turn.active_player, 1)


if __name__ == '__main__':
    unittest.main()
