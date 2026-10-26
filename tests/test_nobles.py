import unittest

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
        player.cards['Ruby'].append(Card('card', 1, 'Ruby', 1))
        noble = Noble('noble', 3, {'Ruby': 4})
        player.nobles.append(noble)
        self.assertEqual(player.points, 4)
        self.assertEqual(player.discounts, {'Ruby': 1})
        self.assertEqual(state.players[1].nobles, [])
        self.assertEqual(State().nobles, [])

    def test_purchase_qualifies_using_new_card_without_spending_bonuses(self):
        state = State()
        player = state.current_player
        player.cards['Ruby'].append(Card('owned', 1, 'Ruby', 0))
        player.tokens = {'Diamond': 1}
        card = Card('buy', 1, 'Ruby', 0, {'Diamond': 1})
        noble = Noble('noble', 3, {'Ruby': 2})
        state.market[1] = [card]
        state.nobles = [noble]
        state.select_card(card)
        state.buy_card()
        self.assertEqual(player.nobles, [noble])
        self.assertEqual(state.nobles, [])
        self.assertEqual(player.discounts, {'Ruby': 2})
        self.assertEqual(player.points, 3)
        self.assertEqual(state.players[1].nobles, [])
        self.assertIn('YOU received noble for 3 points.', state.log)

    def test_tokens_cannot_replace_missing_card_bonuses(self):
        state = State()
        state.current_player.cards['Ruby'].append(Card('ruby', 1, 'Ruby', 0))
        state.current_player.tokens = {'Ruby': 4, 'Onyx': 4, 'Gold': 2}
        nobles = [Noble('short', 3, {'Ruby': 2}),
                  Noble('missing', 3, {'Ruby': 1, 'Onyx': 1})]
        state.nobles = list(nobles)
        state.pass_turn()
        self.assertEqual(state.nobles, nobles)
        self.assertEqual(state.players[0].nobles, [])

    def test_first_qualifying_noble_only_and_cannot_be_awarded_twice(self):
        state = State()
        for player in state.players:
            player.cards['Ruby'].append(Card('ruby', 1, 'Ruby', 0))
        unavailable = Noble('unavailable', 3, {'Onyx': 1})
        first = Noble('first', 3, {'Ruby': 1})
        second = Noble('second', 3, {'Ruby': 1})
        state.nobles = [unavailable, first, second]
        state.select_token('Diamond')
        state.take_tokens()
        self.assertEqual(state.players[0].nobles, [first])
        self.assertEqual(state.players[0].tokens, {'Diamond': 1})
        self.assertEqual(state.nobles, [unavailable, second])
        state.pass_turn()
        self.assertEqual(state.players[1].nobles, [second])
        self.assertEqual(state.nobles, [unavailable])

    def test_rejected_action_does_not_award_noble(self):
        state = State()
        noble = Noble('noble', 3, {'Ruby': 1})
        state.nobles = [noble]
        state.current_player.cards['Ruby'].append(Card('ruby', 1, 'Ruby', 0))
        with self.assertRaises(ValueError):
            state.take_tokens()
        self.assertEqual(state.nobles, [noble])
        self.assertEqual(state.current_player.nobles, [])

    def test_computer_noble_can_end_game_and_change_winner(self):
        state = State()
        state.turn.active_player = 1
        state.players[0].cards['Onyx'].append(Card('human', 3, 'Onyx', 14))
        state.current_player.cards['Ruby'].append(Card('computer', 3, 'Ruby', 12))
        noble = Noble('noble', 3, {'Ruby': 1})
        state.nobles = [noble]
        state.pass_turn()
        self.assertTrue(state.turn.finished)
        self.assertEqual(state.turn.winner, 1)
        self.assertEqual(state.players[1].nobles, [noble])
        with self.assertRaises(ValueError):
            state.pass_turn()
        self.assertEqual(state.players[1].nobles, [noble])

    def test_noble_points_count_toward_final_round(self):
        state = State()
        player = state.current_player
        player.cards['Ruby'].append(Card('card', 3, 'Ruby', 12))
        state.nobles = [Noble('noble', 3, {'Ruby': 1})]
        state.pass_turn()
        self.assertTrue(state.turn.final_round)
        self.assertFalse(state.turn.finished)
        state.pass_turn()
        self.assertTrue(state.turn.finished)
        self.assertEqual(state.turn.winner, 0)


if __name__ == '__main__':
    unittest.main()
