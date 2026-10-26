import unittest

from ai.greedy import GreedyAI
from game.constants import DIAMOND, SAPPHIRE, EMERALD, RUBY, ONYX, GOLD
from game import Card, State


class GreedyAITests(unittest.TestCase):
    def setUp(self):
        self.state = State()
        self.player = self.state.current_player

    def test_replaces_pending_selection_before_collecting(self):
        self.state.market[1] = [Card('target', 1, EMERALD, 0, {RUBY: 1})]
        self.state.selection.select_token(DIAMOND, self.state)
        GreedyAI().play_turn(self.state)
        self.assertEqual(self.player.tokens, {RUBY: 1})
        self.assertEqual(self.state.selection.tokens, {})
        self.assertIsNone(self.state.selection.card)

    def test_buys_an_already_selected_card_without_toggling_it_off(self):
        card = Card('free', 1, RUBY, 1, {})
        self.state.market[1] = [card]
        self.state.selection.select_card(card, self.state)
        GreedyAI().play_turn(self.state)
        self.assertEqual(self.player.cards[RUBY], [card])
        self.assertIsNone(self.state.selection.card)
        self.assertEqual(self.state.turn.active_player, 1)

    def test_buys_highest_points_before_cheapest(self):
        cheap = Card("cheap", 1, RUBY, 1, {})
        valuable = Card("valuable", 2, EMERALD, 3, {DIAMOND: 2})
        self.state.market[1] = [cheap]
        self.state.market[2] = [valuable]
        self.player.tokens = {DIAMOND: 2}
        GreedyAI().play_turn(self.state)
        self.assertEqual(self.player.cards[EMERALD], [valuable])
        self.assertEqual(self.player.tokens, {})
        self.assertEqual(self.state.turn.active_player, 1)

    def test_buys_card_affordable_with_gold(self):
        card = Card('wild', 2, EMERALD, 3, {DIAMOND: 1, RUBY: 1})
        self.state.market[2] = [card]
        self.player.tokens = {GOLD: 2}
        GreedyAI().play_turn(self.state)
        self.assertEqual(self.player.cards[EMERALD], [card])
        self.assertEqual(self.player.tokens, {})

    def test_buys_own_reserved_card(self):
        card = Card('reserved', 2, EMERALD, 3, {RUBY: 1})
        self.player.reserved_cards.append(card)
        self.player.tokens = {GOLD: 1}
        GreedyAI().play_turn(self.state)
        self.assertEqual(self.player.cards[EMERALD], [card])
        self.assertEqual(self.player.reserved_cards, [])
        self.assertEqual(self.player.tokens, {})

    def test_equal_points_use_discounted_payment(self):
        self.player.add_card(Card("owned", 1, RUBY, 0, {}))
        expensive = Card("expensive", 1, EMERALD, 1, {DIAMOND: 2})
        discounted = Card("discounted", 1, ONYX, 1, {RUBY: 2})
        self.state.market[1] = [expensive, discounted]
        self.player.tokens = {DIAMOND: 2, RUBY: 1}
        GreedyAI().play_turn(self.state)
        self.assertIn(discounted, self.player.cards[ONYX])
        self.assertEqual(self.player.tokens, {DIAMOND: 2})

    def test_closest_card_accounts_for_owned_tokens_and_discounts(self):
        self.player.add_card(Card("owned", 1, RUBY, 0, {}))
        self.player.tokens = {RUBY: 2}
        self.state.market[1] = [
            Card("far", 1, ONYX, 0, {DIAMOND: 2}),
            Card("near", 1, EMERALD, 0, {RUBY: 4}),
        ]
        GreedyAI().play_turn(self.state)
        self.assertEqual(self.player.tokens, {RUBY: 3, DIAMOND: 1})

    def test_prefers_fewer_collection_turns_over_fewer_tokens(self):
        self.state.market[1] = [
            Card("slow", 1, ONYX, 0, {RUBY: 3}),
            Card("quick", 1, EMERALD, 0, {DIAMOND: 2, SAPPHIRE: 1, EMERALD: 1}),
        ]
        GreedyAI().play_turn(self.state)
        self.assertEqual(self.player.tokens, {DIAMOND: 1, SAPPHIRE: 1, EMERALD: 1})

    def test_turn_estimate_accounts_for_three_token_limit(self):
        self.state.market[1] = [
            Card("two turns", 1, ONYX, 0,
                 {DIAMOND: 1, SAPPHIRE: 1, EMERALD: 1, RUBY: 1}),
            Card("one turn", 1, EMERALD, 0, {ONYX: 1, RUBY: 1}),
        ]
        GreedyAI().play_turn(self.state)
        self.assertEqual(self.player.tokens, {DIAMOND: 1, RUBY: 1, ONYX: 1})

    def test_spare_picks_skip_duplicate_token_types_and_use_next_targets(self):
        self.state.market[1] = [
            Card("first", 1, ONYX, 0, {RUBY: 1}),
            Card("second", 1, EMERALD, 0, {RUBY: 1, SAPPHIRE: 1}),
            Card("third", 1, DIAMOND, 0, {EMERALD: 2, ONYX: 1}),
        ]
        self.state.supply[ONYX] = 1
        GreedyAI().play_turn(self.state)
        self.assertEqual(self.player.tokens, {RUBY: 1, SAPPHIRE: 1, ONYX: 1})

    def test_spare_picks_respect_inventory_capacity(self):
        self.player.tokens = {ONYX: 8}
        self.state.market[1] = [
            Card("first", 1, ONYX, 0, {RUBY: 1}),
            Card("second", 1, EMERALD, 0, {SAPPHIRE: 1, DIAMOND: 1}),
        ]
        self.state.supply[SAPPHIRE] = 1
        GreedyAI().play_turn(self.state)
        self.assertEqual(self.player.tokens, {ONYX: 8, RUBY: 1, SAPPHIRE: 1})

    def test_takes_three_scarcest_needed_token_types(self):
        self.state.market[1] = [Card("target", 1, ONYX, 1,
                                     {DIAMOND: 1, SAPPHIRE: 1, EMERALD: 1, RUBY: 1})]
        self.state.supply.update(Diamond=4, Sapphire=3, Emerald=1, Ruby=2)
        GreedyAI().play_turn(self.state)
        self.assertEqual(self.player.tokens, {EMERALD: 1, RUBY: 1, SAPPHIRE: 1})

    def test_capacity_limits_collection_to_scarcest_token_type(self):
        self.player.tokens = {ONYX: 9}
        self.state.market[1] = [Card("target", 1, EMERALD, 0, {DIAMOND: 1, RUBY: 1})]
        self.state.supply[RUBY] = 1
        GreedyAI().play_turn(self.state)
        self.assertEqual(self.player.tokens, {ONYX: 9, RUBY: 1})

    def test_skips_blocked_target_and_takes_only_one_of_each_token_type(self):
        self.state.supply[DIAMOND] = 0
        self.state.market[1] = [
            Card("blocked", 1, ONYX, 0, {DIAMOND: 1}),
            Card("available", 1, EMERALD, 0, {RUBY: 2}),
        ]
        GreedyAI().play_turn(self.state)
        self.assertEqual(self.player.tokens, {RUBY: 1})

    def test_passes_when_no_useful_collection_is_possible(self):
        for situation in ("empty market", "empty bank", "full inventory"):
            with self.subTest(situation=situation):
                state = State()
                if situation != "empty market":
                    state.market[1] = [Card("target", 1, EMERALD, 0, {RUBY: 1})]
                if situation == "empty bank":
                    state.supply = {}
                if situation == "full inventory":
                    state.current_player.tokens = {DIAMOND: 10}
                GreedyAI().play_turn(state)
                self.assertEqual(state.turn.consecutive_passes, 1)
                self.assertEqual(state.turn.active_player, 1)


if __name__ == '__main__':
    unittest.main()
