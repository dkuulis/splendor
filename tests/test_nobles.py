from pathlib import Path
import unittest

from game import Card, Noble, State
from game.initialize import create_initial_state, create_nobles


class NobleTests(unittest.TestCase):
    def test_definitions_match_supplied_list(self):
        definitions = Path(__file__).resolve().parents[1] / 'game' / 'nobles.txt'
        expected = {}
        for line in definitions.read_text().splitlines():
            if not line or line.startswith('#'):
                continue
            filename, points, requirements = line.split('|')
            counts = {}
            for requirement in requirements.split(','):
                token, amount = requirement.split(':')
                counts[token.strip()] = int(amount)
            expected[Path(filename.strip()).stem] = (int(points), counts)
        nobles = create_nobles()
        self.assertEqual(len(nobles), 10)
        self.assertEqual({noble.id: (noble.points, noble.requirements)
                          for noble in nobles}, expected)

    def test_setup_deals_three_unique_nobles_repeatably(self):
        first = create_initial_state(seed=42)
        second = create_initial_state(seed=42)
        self.assertEqual(len(first.nobles), 3)
        self.assertEqual(len({noble.id for noble in first.nobles}), 3)
        self.assertEqual([noble.id for noble in first.nobles],
                         [noble.id for noble in second.nobles])
        first.nobles[0].requirements.clear()
        self.assertTrue(second.nobles[0].requirements)
        self.assertTrue(all(player.nobles == {} for player in first.players))

    def test_owned_nobles_score_without_granting_discounts(self):
        state = State()
        player = state.current_player
        player.cards['card'] = Card('card', 1, 'Ruby', 1)
        noble = Noble('noble', 3, {'Ruby': 4})
        player.nobles[noble.id] = noble
        self.assertEqual(player.points, 4)
        self.assertEqual(player.discounts, {'Ruby': 1})
        self.assertEqual(state.players[1].nobles, {})
        self.assertEqual(State().nobles, [])

    def test_noble_points_count_toward_final_round(self):
        state = State()
        player = state.current_player
        player.cards['card'] = Card('card', 3, 'Ruby', 12)
        player.nobles['noble'] = Noble('noble', 3, {'Ruby': 4})
        state.pass_turn()
        self.assertTrue(state.turn.final_round)
        self.assertFalse(state.turn.finished)
        state.pass_turn()
        self.assertTrue(state.turn.finished)
        self.assertEqual(state.turn.winner, 0)


if __name__ == '__main__':
    unittest.main()
