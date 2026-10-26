import unittest

from game.selection import Selection

from game.constants import GEMS, DIAMOND, RUBY, ONYX, GOLD
from game import Card, Noble, State
from game.initialize import create_initial_state


class NobleTests(unittest.TestCase):
    def test_setup_deals_three_unique_nobles_repeatably(self):
        first = create_initial_state(seed=42)
        second = create_initial_state(seed=42)
        self.assertEqual(len(first.nobles), 3)
        self.assertEqual(len({noble.id for noble in first.nobles}), 3)
        self.assertEqual([noble.id for noble in first.nobles],
                         [noble.id for noble in second.nobles])
        first.nobles[0].requirements.clear()
        self.assertTrue(second.nobles[0].requirements)
        self.assertTrue(all(player.nobles == [] for player in first.players))

    def test_owned_nobles_score_without_granting_discounts(self):
        state = State()
        player = state.current_player
        player.add_card(Card('card', 1, RUBY, 1, {}))
        noble = Noble('noble', 3, {RUBY: 4})
        player.nobles.append(noble)
        self.assertEqual(player.points, 4)
        self.assertEqual(player.discounts, {**dict.fromkeys(GEMS, 0), RUBY: 1})
        self.assertEqual(state.players[1].nobles, [])
        self.assertEqual(State().nobles, [])

    def test_purchase_qualifies_using_new_card_without_spending_bonuses(self):
        state = State()
        selection = Selection()
        player = state.current_player
        player.add_card(Card('owned', 1, RUBY, 0, {}))
        player.tokens = {DIAMOND: 1}
        card = Card('buy', 1, RUBY, 0, {DIAMOND: 1})
        noble = Noble('noble', 3, {RUBY: 2})
        state.market[1] = [card]
        state.nobles = [noble]
        selection.select_card(card, state)
        state.buy_card(card)
        self.assertEqual(player.nobles, [noble])
        self.assertEqual(state.nobles, [])
        self.assertEqual(player.discounts, {**dict.fromkeys(GEMS, 0), RUBY: 2})
        self.assertEqual(player.points, 3)
        self.assertEqual(state.players[1].nobles, [])

    def test_tokens_cannot_replace_missing_card_bonuses(self):
        state = State()
        state.current_player.add_card(Card('ruby', 1, RUBY, 0, {}))
        state.current_player.tokens = {RUBY: 4, ONYX: 4, GOLD: 2}
        nobles = [Noble('short', 3, {RUBY: 2}),
                  Noble('missing', 3, {RUBY: 1, ONYX: 1})]
        state.nobles = list(nobles)
        state.pass_turn()
        self.assertEqual(state.nobles, nobles)
        self.assertEqual(state.players[0].nobles, [])

    def test_first_qualifying_noble_only_and_cannot_be_awarded_twice(self):
        state = State()
        selection = Selection()
        for player in state.players:
            player.add_card(Card('ruby', 1, RUBY, 0, {}))
        unavailable = Noble('unavailable', 3, {ONYX: 1})
        first = Noble('first', 3, {RUBY: 1})
        second = Noble('second', 3, {RUBY: 1})
        state.nobles = [unavailable, first, second]
        selection.select_token(DIAMOND, state)
        state.take_tokens(selection.tokens)
        self.assertEqual(state.players[0].nobles, [first])
        self.assertEqual(state.players[0].tokens, {DIAMOND: 1})
        self.assertEqual(state.nobles, [unavailable, second])
        state.pass_turn()
        self.assertEqual(state.players[1].nobles, [second])
        self.assertEqual(state.nobles, [unavailable])

    def test_checking_disallowed_action_does_not_award_noble(self):
        state = State()
        selection = Selection()
        noble = Noble('noble', 3, {RUBY: 1})
        state.nobles = [noble]
        state.current_player.add_card(Card('ruby', 1, RUBY, 0, {}))
        selection.tokens = {RUBY: 3}
        self.assertFalse(selection.can_take_tokens(state))
        self.assertEqual(state.nobles, [noble])
        self.assertEqual(state.current_player.nobles, [])

    def test_computer_noble_can_end_game_and_change_winner(self):
        state = State()
        selection = Selection()
        state.turn.active_player = 1
        state.players[0].add_card(Card('human', 3, ONYX, 14, {}))
        state.current_player.add_card(Card('computer', 3, RUBY, 12, {}))
        noble = Noble('noble', 3, {RUBY: 1})
        state.nobles = [noble]
        state.pass_turn()
        self.assertTrue(state.turn.finished)
        self.assertEqual(state.turn.winner, 1)
        self.assertEqual(state.players[1].nobles, [noble])
        self.assertFalse(selection.can_pass_turn(state))
        self.assertEqual(state.players[1].nobles, [noble])

    def test_noble_points_count_toward_final_round(self):
        state = State()
        player = state.current_player
        player.add_card(Card('card', 3, RUBY, 12, {}))
        state.nobles = [Noble('noble', 3, {RUBY: 1})]
        state.pass_turn()
        self.assertTrue(state.turn.final_round)
        self.assertFalse(state.turn.finished)
        state.pass_turn()
        self.assertTrue(state.turn.finished)
        self.assertEqual(state.turn.winner, 0)


if __name__ == '__main__':
    unittest.main()
