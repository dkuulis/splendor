import pickle
import unittest
from unittest.mock import patch

from ai.greedy_sim import GreedySimAI
from ai.simulation_search import evaluate as evaluate_state
from game import Card, State
from game.constants import DIAMOND, EMERALD, GOLD, ONYX, RUBY, SAPPHIRE, TOKENS
from game.noble import Noble
from game.selection import Selection
from simulation import State as SimulationState, generate_moves


class GreedySimAITests(unittest.TestCase):
    def setUp(self):
        self.state = State()
        self.selection = Selection()
        self.ai = GreedySimAI()

    def choose(self):
        before = pickle.dumps(self.state)
        self.ai.make_selection(self.state, self.selection)
        self.assertEqual(pickle.dumps(self.state), before)
        self.assertTrue(self.selection.can_perform_action(self.state))

    def test_buys_highest_points_and_replaces_pending_choice(self):
        cheap = Card('cheap', 1, RUBY, 1, {})
        valuable = Card('valuable', 2, EMERALD, 3, {DIAMOND: 2})
        self.state.market[1] = [cheap]
        self.state.market[2] = [valuable]
        self.state.current_player.tokens = {DIAMOND: 2}
        self.selection.select_card(cheap, self.state)
        self.choose()
        self.assertIs(self.selection.card, valuable)
        self.assertEqual(self.selection.action_kind, 'buy')

    def test_evaluates_candidate_positions_after_executing_moves(self):
        card = Card('purchase', 1, RUBY, 2, {})
        self.state.market[1] = [card]
        scores = []
        evaluate = evaluate_state

        def record(position, player_index):
            score = evaluate(position, player_index)
            scores.append(score)
            return score

        with patch('ai.greedy_sim.evaluate', side_effect=record):
            self.choose()
        self.assertIn((2, 1), [score[:2] for score in scores])
        self.assertIn((0, 0), [score[:2] for score in scores])
        self.assertIs(self.selection.card, card)

    def test_equal_point_purchases_prefer_cheaper_payment(self):
        expensive = Card('expensive', 1, RUBY, 1, {DIAMOND: 2})
        cheap = Card('cheap', 1, EMERALD, 1, {DIAMOND: 1})
        self.state.market[1] = [expensive, cheap]
        self.state.current_player.tokens = {DIAMOND: 3}
        self.choose()
        self.assertIs(self.selection.card, cheap)

    def test_prefers_immediate_noble_points(self):
        self.state.current_player.add_card(Card('owned', 1, RUBY, 0, {}))
        noble_card = Card('noble', 1, RUBY, 0, {})
        points_card = Card('points', 2, ONYX, 2, {})
        self.state.market[1] = [noble_card]
        self.state.market[2] = [points_card]
        self.state.nobles = [Noble('noble', 3, {RUBY: 2})]
        self.choose()
        self.assertIs(self.selection.card, noble_card)

    def test_buys_reserved_card_with_gold_for_second_player(self):
        self.state.turn.active_player = 1
        card = Card('reserved', 2, RUBY, 3, {DIAMOND: 1})
        self.state.current_player.reserved_cards = [card]
        self.state.current_player.tokens = {GOLD: 1}
        self.choose()
        self.assertIs(self.selection.card, card)
        self.assertEqual(self.selection.action_kind, 'buy')

    def test_pair_can_make_target_affordable_in_one_move(self):
        self.state.supply[GOLD] = 0
        self.state.market[1] = [Card('target', 1, EMERALD, 0, {RUBY: 2})]
        self.choose()
        self.assertEqual(self.selection.tokens, {RUBY: 2})

    def test_distinct_take_advances_target(self):
        self.state.supply[GOLD] = 0
        self.state.market[1] = [Card('target', 1, ONYX, 0,
                                     {DIAMOND: 1, SAPPHIRE: 1, EMERALD: 1})]
        self.choose()
        self.assertEqual(self.selection.tokens, {DIAMOND: 1, SAPPHIRE: 1, EMERALD: 1})

    def test_reservation_can_supply_useful_wildcard(self):
        target = Card('target', 1, EMERALD, 1, {RUBY: 1})
        self.state.market[1] = [target]
        self.state.supply = {GOLD: 1}
        self.choose()
        self.assertEqual(self.selection.action_kind, 'reserve')
        self.assertIs(self.selection.card, target)

    def test_scores_every_generated_move_including_returns(self):
        self.state.current_player.tokens = {ONYX: 10}
        self.state.market[1] = [Card('target', 1, EMERALD, 0, {RUBY: 1})]
        moves = generate_moves(SimulationState.from_game(self.state), 0)
        self.assertTrue(any(any(amount < 0 for amount in move.tokens) for move in moves))
        before = pickle.dumps(self.state)
        with patch('ai.greedy_sim.evaluate', side_effect=range(len(moves))) as evaluate, \
                patch('ai.simulation_search.update_selection_from_move') as update:
            self.ai.make_selection(self.state, self.selection)
        self.assertEqual(evaluate.call_count, len(moves))
        update.assert_called_once()
        chosen = update.call_args.args[0]
        self.assertEqual((chosen.kind, chosen.card_index, chosen.tokens),
                         (moves[-1].kind, moves[-1].card_index, moves[-1].tokens))
        self.assertEqual(pickle.dumps(self.state), before)

    def test_passes_when_no_moves_are_generated(self):
        self.state.supply = {}
        self.choose()
        self.assertEqual(self.selection.action_kind, 'pass')

    def test_evaluation_rewards_gold_and_discounts_toward_targets(self):
        self.state.market[1] = [Card('target', 1, EMERALD, 0, {RUBY: 3})]
        position = SimulationState.from_game(self.state)
        before = evaluate_state(position, 0)
        position.players[0].tokens[TOKENS.index(GOLD)] = 1
        position.players[0].token_count = 1
        self.assertGreater(evaluate_state(position, 0), before)
        with_gold = evaluate_state(position, 0)
        position.players[0].discounts[TOKENS.index(RUBY)] = 1
        self.assertGreater(evaluate_state(position, 0), with_gold)

    def test_evaluates_market_replacements_from_copied_deck(self):
        first = Card('first', 1, RUBY, 1, {})
        second = Card('second', 2, EMERALD, 1, {})
        self.state.market[1] = [first]
        self.state.market[2] = [second]
        hidden = Card('hidden', 1, ONYX, 5, {})
        self.state.decks[1] = [hidden]
        def evaluate(position, player_index):
            return max(position.cards[index].points
                       for row in position.market_indices for index in row)

        with patch('ai.greedy_sim.evaluate', side_effect=evaluate):
            self.choose()
        self.assertIs(self.selection.card, first)
