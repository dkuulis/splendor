import math
import pickle
import unittest

from ai.greedy_sim import GreedySimAI
from ai.minimax import MinimaxAI, evaluate_position, score_move
from game import Card, State
from game.constants import EMERALD, ONYX, RUBY
from game.noble import Noble
from game.selection import Selection
from simulation import State as SimulationState


class MinimaxAITests(unittest.TestCase):
    def choose(self, state):
        selection = Selection()
        before = pickle.dumps(state)
        MinimaxAI().make_selection(state, selection)
        self.assertEqual(pickle.dumps(state), before)
        self.assertTrue(selection.can_perform_action(state))
        return selection

    def test_blocks_opponents_winning_reply_instead_of_greedy_points(self):
        state = State()
        tempting = Card('tempting', 1, EMERALD, 2, {})
        threat = Card('threat', 1, RUBY, 0, {})
        state.market[1] = [tempting, threat]
        state.players[1].add_card(Card('points', 1, ONYX, 12, {}))
        state.players[1].add_card(Card('bonus', 1, RUBY, 0, {}))
        state.nobles = [Noble('noble', 3, {RUBY: 2})]
        greedy = Selection()
        GreedySimAI().make_selection(state, greedy)
        self.assertIs(greedy.card, tempting)
        selection = self.choose(state)
        self.assertIs(selection.card, threat)
        self.assertEqual(selection.action_kind, 'buy')

    def test_second_player_takes_immediate_win(self):
        state = State()
        state.turn.active_player = 1
        state.current_player.add_card(Card('points', 1, ONYX, 14, {}))
        winning = Card('winning', 1, RUBY, 1, {})
        state.market[1] = [Card('bonus', 1, EMERALD, 0, {}), winning]
        selection = self.choose(state)
        self.assertIs(selection.card, winning)

    def test_terminal_results_use_points_and_fewer_cards(self):
        state = SimulationState()
        state.players[0].points = state.players[1].points = 15
        state.players[0].card_count = 2
        state.players[1].card_count = 3
        self.assertEqual(evaluate_position(state, 0, 0)[0], 1)
        self.assertEqual(evaluate_position(state, 1, 0)[0], -1)
        state.players[1].card_count = 2
        self.assertEqual(evaluate_position(state, 0, 0), (0, 0, 0, 0, 0, 0))

    def test_empty_targets_produce_no_nan(self):
        state = SimulationState()
        score = evaluate_position(state, 0, 1)
        self.assertTrue(all(not math.isnan(value) for value in score))
        self.assertEqual(score_move(state, 0), score)

    def test_passes_with_no_moves(self):
        state = State()
        state.supply = {}
        self.assertEqual(self.choose(state).action_kind, 'pass')

    def test_reply_search_restores_simulated_position(self):
        source = State()
        source.market[1] = [Card('first', 1, RUBY, 1, {}),
                            Card('second', 1, EMERALD, 0, {})]
        state = SimulationState.from_game(source)
        before = pickle.dumps(state)
        score_move(state, 0)
        for row in state.market_indices:
            row.sort()
        self.assertEqual(pickle.dumps(state), before)
