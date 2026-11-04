"""Run headless matches between registered AI strategies."""

import argparse
import random

from ai import STRATEGIES
from game.initialize import create_initial_state
from game.selection import Selection


def positive_int(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return number


def play_game(strategies, seed, max_turns):
    """Play one game in seat order, checking choices before dispatch."""
    state = create_initial_state(seed=seed)
    for player in state.players:
        player.is_ai = True
    selection = Selection()
    turns = 0
    error = None
    while not state.turn.finished and turns < max_turns:
        seat = state.turn.active_player
        try:
            strategies[seat].make_selection(state, selection)
        except Exception as exc:
            # Isolate a failed strategy so the rest of a batch still runs.
            error = f"seat {seat + 1} strategy raised {type(exc).__name__}: {exc}"
            break
        if not selection.can_perform_action(state):
            error = f"seat {seat + 1} selected an invalid {selection.action_kind} action"
            break
        selection.perform_action(state)
        # Take/Reserve and their required Return count as a single turn.
        if not selection.returning:
            turns += 1
    return {
        "status": "error" if error else "finished" if state.turn.finished else "limit",
        "winner": state.turn.winner,
        "scores": [player.points for player in state.players],
        "turns": turns,
        "error": error,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ai1", choices=STRATEGIES, default="greedy",
                        help="First AI (default: greedy)")
    parser.add_argument("--ai2", choices=STRATEGIES, default="greedy2",
                        help="Second AI (default: greedy2)")
    parser.add_argument("--rounds", "--games", type=positive_int, default=10,
                        help="Number of games (default: 10); starting AI alternates")
    parser.add_argument("--seed", type=int, help="Seed for repeatable deals")
    parser.add_argument("--max-turns", type=positive_int, default=1000,
                        help="Stop an unfinished game after this many player turns (default: 1000)")
    args = parser.parse_args(argv)

    seed = args.seed if args.seed is not None else random.randrange(2 ** 32)
    names = [args.ai1, args.ai2]
    wins = [0, 0]
    scores = [0, 0]
    draws = limits = errors = completed = total_turns = 0
    print(f"AI 1: {names[0]} | AI 2: {names[1]} | Games: {args.rounds} | Seed: {seed}", flush=True)
    for game in range(args.rounds):
        seats = [0, 1] if game % 2 == 0 else [1, 0]
        strategies = [STRATEGIES[names[index]]() for index in seats]
        result = play_game(strategies, seed + game, args.max_turns)
        game_scores = [0, 0]
        for seat, index in enumerate(seats):
            game_scores[index] = result["scores"][seat]
        if result["status"] == "finished":
            completed += 1
            total_turns += result["turns"]
            for index in range(2):
                scores[index] += game_scores[index]
            if result["winner"] is None:
                draws += 1
                outcome = "draw"
            else:
                winner = seats[result["winner"]]
                wins[winner] += 1
                outcome = f"AI {winner + 1} wins"
        elif result["status"] == "limit":
            limits += 1
            outcome = "turn limit (unfinished)"
        else:
            errors += 1
            outcome = f"error: {result['error']}"
        print(f"Game {game + 1}: {outcome}; score {game_scores[0]}–{game_scores[1]}; "
              f"{result['turns']} turns; AI {seats[0] + 1} started; seed {seed + game}", flush=True)

    print(f"\nCompleted: {completed}/{args.rounds} | Draws: {draws} | "
          f"Turn limits: {limits} | Errors: {errors}")
    for index, name in enumerate(names):
        rate = f"{100 * wins[index] / completed:.1f}%" if completed else "n/a"
        average = f"{scores[index] / completed:.2f}" if completed else "n/a"
        print(f"AI {index + 1} ({name}): {wins[index]} wins ({rate}); average score {average}")
    if completed:
        print(f"Average turns: {total_turns / completed:.1f} (completed games only)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
