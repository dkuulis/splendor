import pickle
import unittest

from game.selection import Selection

from ai.greedy import GreedyAI
from game.constants import DIAMOND, SAPPHIRE, EMERALD, RUBY, ONYX, GOLD
from game import Card, State


class GreedyAITests(unittest.TestCase):
    def setUp(self):
        self.state = State()
        self.selection = Selection()
        self.player = self.state.current_player

    def make_selection(self):
        # Snapshot the whole state, including decks, to catch execution by AI.
        before = pickle.dumps(self.state)
        GreedyAI().make_selection(self.state, self.selection)
        self.assertEqual(pickle.dumps(self.state), before)
        self.assertTrue(self.selection.can_perform_action(self.state))

    def test_replaces_pending_selection_before_selecting_gems(self):
        self.state.market[1] = [Card('target', 1, EMERALD, 0, {RUBY: 1})]
        self.selection.select_token(DIAMOND, self.state)
        self.make_selection()
        self.assertEqual(self.player.tokens, {})
        self.assertEqual(self.selection.tokens, {RUBY: 1})
        self.assertIsNone(self.selection.card)

    def test_selects_an_already_selected_card_without_toggling_it_off(self):
        card = Card('free', 1, RUBY, 1, {})
        self.state.market[1] = [card]
        self.selection.select_card(card, self.state)
        self.make_selection()
        self.assertIs(self.selection.card, card)
        self.assertEqual(self.selection.tokens, {})
        self.assertEqual(self.state.turn.active_player, 0)

    def test_selects_highest_points_before_cheapest(self):
        cheap = Card("cheap", 1, RUBY, 1, {})
        valuable = Card("valuable", 2, EMERALD, 3, {DIAMOND: 2})
        self.state.market[1] = [cheap]
        self.state.market[2] = [valuable]
        self.player.tokens = {DIAMOND: 2}
        self.make_selection()
        self.assertIs(self.selection.card, valuable)
        self.assertEqual(self.selection.tokens, {})
        self.assertEqual(self.state.turn.active_player, 0)

    def test_selects_card_affordable_with_gold(self):
        card = Card('wild', 2, EMERALD, 3, {DIAMOND: 1, RUBY: 1})
        self.state.market[2] = [card]
        self.player.tokens = {GOLD: 2}
        self.make_selection()
        self.assertIs(self.selection.card, card)
        self.assertEqual(self.selection.tokens, {})

    def test_selects_own_reserved_card(self):
        card = Card('reserved', 2, EMERALD, 3, {RUBY: 1})
        self.player.reserved_cards.append(card)
        self.player.tokens = {GOLD: 1}
        self.make_selection()
        self.assertIs(self.selection.card, card)
        self.assertEqual(self.selection.tokens, {})
        self.assertEqual(self.player.reserved_cards, [card])

    def test_equal_points_use_discounted_payment(self):
        self.player.add_card(Card("owned", 1, RUBY, 0, {}))
        expensive = Card("expensive", 1, EMERALD, 1, {DIAMOND: 2})
        discounted = Card("discounted", 1, ONYX, 1, {RUBY: 2})
        self.state.market[1] = [expensive, discounted]
        self.player.tokens = {DIAMOND: 2, RUBY: 1}
        self.make_selection()
        self.assertIs(self.selection.card, discounted)
        self.assertEqual(self.selection.tokens, {})

    def test_closest_card_accounts_for_owned_tokens_and_discounts(self):
        self.player.add_card(Card("owned", 1, RUBY, 0, {}))
        self.player.tokens = {RUBY: 2}
        self.state.market[1] = [
            Card("far", 1, ONYX, 0, {DIAMOND: 2}),
            Card("near", 1, EMERALD, 0, {RUBY: 4}),
        ]
        self.make_selection()
        self.assertEqual(self.selection.tokens, {RUBY: 1, DIAMOND: 1})

    def test_prefers_fewer_collection_turns_over_fewer_tokens(self):
        self.state.market[1] = [
            Card("slow", 1, ONYX, 0, {RUBY: 3}),
            Card("quick", 1, EMERALD, 0, {DIAMOND: 2, SAPPHIRE: 1, EMERALD: 1}),
        ]
        self.make_selection()
        self.assertEqual(self.selection.tokens, {DIAMOND: 1, SAPPHIRE: 1, EMERALD: 1})

    def test_turn_estimate_accounts_for_three_token_limit(self):
        self.state.market[1] = [
            Card("two turns", 1, ONYX, 0,
                 {DIAMOND: 1, SAPPHIRE: 1, EMERALD: 1, RUBY: 1}),
            Card("one turn", 1, EMERALD, 0, {ONYX: 1, RUBY: 1}),
        ]
        self.make_selection()
        self.assertEqual(self.selection.tokens, {DIAMOND: 1, RUBY: 1, ONYX: 1})

    def test_spare_picks_skip_duplicate_token_types_and_use_next_targets(self):
        self.state.market[1] = [
            Card("first", 1, ONYX, 0, {RUBY: 1}),
            Card("second", 1, EMERALD, 0, {RUBY: 1, SAPPHIRE: 1}),
            Card("third", 1, DIAMOND, 0, {EMERALD: 2, ONYX: 1}),
        ]
        self.state.supply[ONYX] = 1
        self.make_selection()
        self.assertEqual(self.selection.tokens, {RUBY: 1, SAPPHIRE: 1, ONYX: 1})

    def test_spare_picks_respect_inventory_capacity(self):
        self.player.tokens = {ONYX: 8}
        self.state.market[1] = [
            Card("first", 1, ONYX, 0, {RUBY: 1}),
            Card("second", 1, EMERALD, 0, {SAPPHIRE: 1, DIAMOND: 1}),
        ]
        self.state.supply[SAPPHIRE] = 1
        self.make_selection()
        self.assertEqual(self.selection.tokens, {RUBY: 1, SAPPHIRE: 1})

    def test_selects_three_scarcest_needed_token_types(self):
        self.state.market[1] = [Card("target", 1, ONYX, 1,
                                     {DIAMOND: 1, SAPPHIRE: 1, EMERALD: 1, RUBY: 1})]
        self.state.supply.update(Diamond=4, Sapphire=3, Emerald=1, Ruby=2)
        self.make_selection()
        self.assertEqual(self.selection.tokens, {EMERALD: 1, RUBY: 1, SAPPHIRE: 1})

    def test_capacity_limits_collection_to_scarcest_token_type(self):
        self.player.tokens = {ONYX: 9}
        self.state.market[1] = [Card("target", 1, EMERALD, 0, {DIAMOND: 1, RUBY: 1})]
        self.state.supply[RUBY] = 1
        self.make_selection()
        self.assertEqual(self.selection.tokens, {RUBY: 1})

    def test_skips_blocked_target_and_takes_only_one_of_each_token_type(self):
        self.state.supply[DIAMOND] = 0
        self.state.market[1] = [
            Card("blocked", 1, ONYX, 0, {DIAMOND: 1}),
            Card("available", 1, EMERALD, 0, {RUBY: 2}),
        ]
        self.make_selection()
        self.assertEqual(self.selection.tokens, {RUBY: 1})

    def test_selects_pass_when_no_useful_collection_is_possible(self):
        for situation in ("empty market", "empty bank", "full inventory"):
            with self.subTest(situation=situation):
                state = State()
                selection = Selection()
                if situation != "empty market":
                    state.market[1] = [Card("target", 1, EMERALD, 0, {RUBY: 1})]
                if situation == "empty bank":
                    state.supply = {}
                if situation == "full inventory":
                    state.current_player.tokens = {DIAMOND: 10}
                before = pickle.dumps(state)
                GreedyAI().make_selection(state, selection)
                self.assertEqual(pickle.dumps(state), before)
                self.assertEqual(selection.action_kind, 'pass')
                self.assertTrue(selection.can_perform_action(state))


if __name__ == '__main__':
    unittest.main()
