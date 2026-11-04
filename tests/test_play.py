import contextlib
import io
import unittest
from unittest.mock import patch

import play
from ai import GreedyAI, Greedy2AI, GreedySimAI, PassOnlyAI
from game import Card, State
from game.constants import RUBY


class SelfPlayTests(unittest.TestCase):
    def test_two_passes_finish_as_draw(self):
        result = play.play_game([PassOnlyAI(), PassOnlyAI()], 7, 10)
        self.assertEqual(result["status"], "finished")
        self.assertIsNone(result["winner"])
        self.assertEqual(result["scores"], [0, 0])
        self.assertEqual(result["turns"], 2)

    def test_turn_limit_is_unfinished(self):
        result = play.play_game([PassOnlyAI(), PassOnlyAI()], 7, 1)
        self.assertEqual(result["status"], "limit")
        self.assertEqual(result["turns"], 1)

    def test_seed_repeats_a_real_match(self):
        first = play.play_game([GreedyAI(), Greedy2AI()], 12, 300)
        second = play.play_game([GreedyAI(), Greedy2AI()], 12, 300)
        self.assertEqual(first, second)
        self.assertEqual(first["status"], "finished")

    def test_invalid_selection_is_reported_before_execution(self):
        class InvalidAI:
            def make_selection(self, state, selection):
                selection.tokens = {RUBY: 100}

        state = State()
        with patch("play.create_initial_state", return_value=state):
            result = play.play_game([InvalidAI(), PassOnlyAI()], 7, 10)
        self.assertEqual(result["status"], "error")
        self.assertIn("seat 1", result["error"])
        self.assertEqual(state.players[0].tokens, {})

    def test_search_ai_completes_previously_crashing_deal(self):
        result = play.play_game([GreedySimAI(), Greedy2AI()], 52, 300)
        self.assertEqual(result["status"], "finished", result["error"])

    def test_strategy_exception_does_not_abort_batch(self):
        class BrokenAI:
            def make_selection(self, state, selection):
                raise KeyError(4)

        output = io.StringIO()
        with patch.dict(play.STRATEGIES, {"broken": BrokenAI}), contextlib.redirect_stdout(output):
            code = play.main(["--rounds", "2", "--ai1", "broken", "--ai2", "pass-only"])
        self.assertEqual(code, 1)
        self.assertIn("Game 2:", output.getvalue())
        self.assertIn("strategy raised KeyError: 4", output.getvalue())
        self.assertIn("Errors: 2", output.getvalue())

    def test_return_finishes_same_turn(self):
        class OverflowAI:
            def make_selection(self, state, selection):
                selection.clear()
                if selection.returning:
                    selection.select_return_token(RUBY, state)
                else:
                    selection.select_token(RUBY, state)
                    selection.select_token(RUBY, state)

        state = State()
        state.players[0].tokens = {RUBY: 9}
        with patch("play.create_initial_state", return_value=state):
            result = play.play_game([OverflowAI(), PassOnlyAI()], 7, 1)
        self.assertEqual(result["status"], "limit")
        self.assertEqual(result["turns"], 1)
        self.assertEqual(state.players[0].token_count, 10)
        self.assertEqual(state.turn.active_player, 1)

    def test_cli_alternates_starter_and_maps_wins_to_ai_identity(self):
        def initial_state(seed):
            state = State()
            state.players[0].add_card(Card("winner", 1, RUBY, 15, {}))
            return state

        output = io.StringIO()
        with patch("play.create_initial_state", side_effect=initial_state) as create, \
                contextlib.redirect_stdout(output):
            code = play.main(["--rounds", "2", "--ai1", "pass-only",
                              "--ai2", "greedy", "--seed", "42"])
        self.assertEqual(code, 0)
        self.assertEqual([call.kwargs["seed"] for call in create.call_args_list], [42, 43])
        report = output.getvalue()
        self.assertIn("AI 1 (pass-only): 1 wins (50.0%)", report)
        self.assertIn("AI 2 (greedy): 1 wins (50.0%)", report)
        self.assertIn("AI 2 started", report)

    def test_errors_are_counted_separately_from_draws(self):
        result = {"status": "error", "winner": None, "scores": [0, 0],
                  "turns": 0, "error": "invalid take"}
        output = io.StringIO()
        with patch("play.play_game", return_value=result), contextlib.redirect_stdout(output):
            code = play.main(["--rounds", "2"])
        self.assertEqual(code, 1)
        self.assertIn("Draws: 0 | Turn limits: 0 | Errors: 2", output.getvalue())
        self.assertIn("average score n/a", output.getvalue())

    def test_invalid_arguments(self):
        for arguments in (["--rounds", "0"], ["--rounds", "-1"],
                          ["--max-turns", "0"], ["--ai1", "manual"],
                          ["--ai2", "unknown"]):
            with self.subTest(arguments=arguments), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    play.main(arguments)
                self.assertEqual(raised.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
