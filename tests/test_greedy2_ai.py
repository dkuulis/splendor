import pickle
import unittest

from ai import Greedy2AI
from game import Card, State
from game.constants import DIAMOND, EMERALD, GOLD, ONYX, RUBY, SAPPHIRE
from game.noble import Noble
from game.selection import Selection


class Greedy2AITests(unittest.TestCase):
    def setUp(self):
        self.state = State()
        self.player = self.state.current_player
        self.player.is_ai = True
        self.selection = Selection()

    def own(self, token, count):
        for index in range(count):
            self.player.add_card(Card(f'owned-{token}-{index}', 1, token, 0, {}))

    def choose(self):
        before = pickle.dumps(self.state)
        Greedy2AI().make_selection(self.state, self.selection)
        self.assertEqual(pickle.dumps(self.state), before)
        self.assertTrue(self.selection.can_perform_action(self.state))

    def test_immediate_noble_points_outweigh_card_points(self):
        self.own(RUBY, 3)
        noble_card = Card('noble', 1, RUBY, 0, {})
        self.state.market[1] = [Card('points', 1, ONYX, 2, {}), noble_card]
        self.state.nobles = [Noble('noble', 3, {RUBY: 4})]
        self.choose()
        self.assertIs(self.selection.card, noble_card)

    def test_reserved_card_can_earn_noble_with_gold_payment(self):
        self.own(RUBY, 3)
        reserved = Card('reserved', 1, RUBY, 0, {DIAMOND: 1})
        self.player.reserved_cards = [reserved]
        self.player.tokens = {GOLD: 1}
        self.state.market[1] = [Card('points', 1, ONYX, 2, {})]
        self.state.nobles = [Noble('noble', 3, {RUBY: 4})]
        self.choose()
        self.assertIs(self.selection.card, reserved)
        self.assertEqual(self.selection.tokens, {})

    def test_counts_only_first_qualifying_noble(self):
        ruby = Card('ruby', 1, RUBY, 0, {})
        onyx = Card('onyx', 1, ONYX, 0, {})
        self.state.market[1] = [ruby, onyx]
        self.state.nobles = [Noble('first', 1, {RUBY: 1}),
                             Noble('second', 5, {RUBY: 1}),
                             Noble('other', 3, {ONYX: 1})]
        self.choose()
        self.assertIs(self.selection.card, onyx)

    def test_prefers_progress_toward_closer_noble_before_cost(self):
        self.own(RUBY, 2)
        closer = Card('closer', 1, RUBY, 0, {DIAMOND: 2})
        self.state.market[1] = [Card('irrelevant', 1, EMERALD, 0, {}),
                                Card('farther', 1, ONYX, 0, {}), closer]
        self.player.tokens = {DIAMOND: 2}
        self.state.nobles = [Noble('far', 3, {ONYX: 4}),
                             Noble('near', 3, {RUBY: 4})]
        self.choose()
        self.assertIs(self.selection.card, closer)

    def test_satisfied_color_and_owned_tokens_do_not_advance_noble(self):
        self.own(RUBY, 4)
        self.player.tokens = {ONYX: 4}
        useful = Card('useful', 1, ONYX, 0, {})
        self.state.market[1] = [Card('satisfied', 1, RUBY, 0, {}), useful]
        self.state.nobles = [Noble('noble', 3, {RUBY: 4, ONYX: 4})]
        self.choose()
        self.assertIs(self.selection.card, useful)

    def test_total_missing_bonuses_determine_noble_distance(self):
        closer = Card('closer', 1, RUBY, 0, {})
        self.state.market[1] = [Card('farther', 1, ONYX, 0, {}), closer]
        self.state.nobles = [Noble('far', 3, {ONYX: 1, DIAMOND: 4}),
                             Noble('near', 3, {RUBY: 2})]
        self.choose()
        self.assertIs(self.selection.card, closer)

    def test_no_nobles_uses_points_then_discounted_cost_then_order(self):
        self.own(RUBY, 1)
        first = Card('first', 1, EMERALD, 2, {RUBY: 2})
        self.state.market[1] = [Card('cheap', 1, ONYX, 1, {}),
                                Card('expensive', 1, ONYX, 2, {DIAMOND: 2}),
                                first, Card('tied', 1, SAPPHIRE, 2, {RUBY: 2})]
        self.player.tokens = {RUBY: 1, DIAMOND: 2}
        self.choose()
        self.assertIs(self.selection.card, first)

    def test_equal_collection_turns_favor_noble_over_missing_gem_count(self):
        self.state.market[1] = [Card('cheap', 1, ONYX, 0, {DIAMOND: 2}),
                                Card('noble', 1, RUBY, 0, {EMERALD: 2, SAPPHIRE: 1})]
        self.state.nobles = [Noble('noble', 3, {RUBY: 4})]
        self.choose()
        self.assertEqual(next(iter(self.selection.tokens)), SAPPHIRE)

    def test_fewer_collection_turns_outrank_noble_progress(self):
        self.state.market[1] = [Card('noble', 1, RUBY, 0, {EMERALD: 2}),
                                Card('quick', 1, DIAMOND, 0, {SAPPHIRE: 1})]
        self.state.nobles = [Noble('noble', 3, {RUBY: 4})]
        self.choose()
        self.assertEqual(next(iter(self.selection.tokens)), SAPPHIRE)

    def test_equal_turn_targets_prefer_closer_noble(self):
        self.state.market[1] = [Card('far', 1, DIAMOND, 0, {EMERALD: 1}),
                                Card('near', 1, RUBY, 0, {SAPPHIRE: 1})]
        self.state.nobles = [Noble('far', 3, {DIAMOND: 4}),
                             Noble('near', 3, {RUBY: 2})]
        self.choose()
        self.assertEqual(next(iter(self.selection.tokens)), SAPPHIRE)

    def test_collection_uses_missing_gems_then_card_order_without_nobles(self):
        self.state.market[1] = [Card('more', 1, DIAMOND, 0, {EMERALD: 1, RUBY: 1}),
                                Card('first', 1, RUBY, 0, {SAPPHIRE: 1}),
                                Card('tied', 1, EMERALD, 0, {DIAMOND: 1})]
        self.choose()
        self.assertEqual(next(iter(self.selection.tokens)), SAPPHIRE)

    def test_collection_reuses_scarcity_spare_picks_and_skips_blocked_targets(self):
        self.state.supply[DIAMOND] = 0
        self.state.supply[SAPPHIRE] = 1
        self.state.market[1] = [Card('blocked', 1, RUBY, 0, {DIAMOND: 1}),
                                Card('useful', 1, RUBY, 0, {EMERALD: 1}),
                                Card('spare', 1, ONYX, 0, {RUBY: 1, SAPPHIRE: 1})]
        self.state.nobles = [Noble('noble', 3, {RUBY: 4})]
        self.selection.select_token(ONYX, self.state)
        self.choose()
        self.assertEqual(self.selection.tokens, {EMERALD: 1, SAPPHIRE: 1, RUBY: 1})

    def test_pass_when_no_useful_collection_or_capacity(self):
        for situation in ('empty market', 'empty bank', 'full inventory'):
            with self.subTest(situation=situation):
                self.setUp()
                if situation != 'empty market':
                    self.state.market[1] = [Card('target', 1, RUBY, 0, {EMERALD: 1})]
                if situation == 'empty bank':
                    self.state.supply = {}
                if situation == 'full inventory':
                    self.player.tokens = {ONYX: 10}
                self.choose()
                self.assertEqual(self.selection.action_kind, 'pass')


if __name__ == '__main__':
    unittest.main()
