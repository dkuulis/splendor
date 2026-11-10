"""Scene behavior without creating a Tk interpreter."""

import struct
import unittest
from pathlib import Path

from app.layout import layout
from game.constants import GOLD, RUBY, DIAMOND, SAPPHIRE, TOKENS
from game.initialize import create_initial_state
from game.selection import Selection


class LayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sizes = {p.stem: struct.unpack('>II', p.read_bytes()[16:24])
                     for p in (Path(__file__).resolve().parents[1] / 'assets').glob('*.png')}

    def setUp(self):
        self.state = create_initial_state()
        self.selection = Selection()

    def scene(self, width=1700, height=1300, manual=True):
        return layout(self.state, self.selection, width, height, self.sizes, manual)

    def test_selection_hides_source_and_keeps_market_and_buttons_fixed(self):
        before, minimum = self.scene()
        card = self.state.market[1][0]
        self.selection.select_card(card, self.state)
        after, selected_minimum = self.scene()
        self.assertFalse(after['market', 1, 0]['visible'])
        self.assertEqual(after['selected-card',]['image'], card.id)
        for key in [('action',), ('restart',), ('market', 1, 1)]:
            self.assertEqual((before[key]['x'], before[key]['y']), (after[key]['x'], after[key]['y']))
        self.assertEqual(minimum, selected_minimum)
        self.selection.select_card(card, self.state)
        self.assertTrue(self.scene()[0]['market', 1, 0]['visible'])

    def test_exhausted_decks_and_empty_market_keep_alignment(self):
        before, _ = self.scene()
        self.state.decks[2].clear()
        self.state.market[2].clear()
        after, _ = self.scene()
        self.assertFalse(after['deck', 2]['visible'])
        self.assertTrue(all(not after['market', 2, slot]['visible'] for slot in range(4)))
        self.assertEqual(before['market', 1, 0], after['market', 1, 0])

    def test_holdings_grow_minimum_width_and_preserve_stack_offsets(self):
        card = self.state.market[1][0]
        card.points = 0  # Exercise wide holdings without requiring a score-60 asset.
        player = self.state.players[0]
        player.cards[card.token] = [card] * 60
        elements, minimum = self.scene()
        self.assertGreater(minimum[0], 1700)
        first = elements['player-card', 0, card.token, 0]
        second = elements['player-card', 0, card.token, 1]
        last = elements['player-card', 0, card.token, 59]
        self.assertEqual(second['x'] - first['x'], 30)
        self.assertLessEqual(last['x'] + 150, minimum[0] - 20)

    def test_return_piles_reduce_holdings_without_reducing_supply(self):
        self.state.players[0].tokens = {RUBY: 4, GOLD: 2, DIAMOND: 4, SAPPHIRE: 2}
        for token, count in self.state.players[0].tokens.items():
            self.state.supply[token] -= count
        self.selection.returning = True
        before, _ = self.scene()
        self.selection.select_return_token(RUBY, self.state)
        self.selection.select_return_token(GOLD, self.state)
        after, _ = self.scene()
        self.assertEqual(before['supply', RUBY], after['supply', RUBY])
        self.assertEqual(after['player-token', 0, RUBY]['image'], 'ruby3')
        self.assertEqual(after['player-token', 0, GOLD]['image'], 'gold')
        self.assertEqual(after['action',]['action'], ('perform_action', ()))
        self.assertTrue(all(after['supply', token]['action'] is None for token in TOKENS))
        self.assertEqual(after['selected-token', GOLD]['action'], ('deselect_token', (GOLD,)))

    def test_results_disable_action_and_highlight_only_winner(self):
        self.state.turn.finished = True
        for winner, result in ((0, 'win'), (1, 'loose'), (None, 'tie')):
            self.state.turn.winner = winner
            elements, _ = self.scene(manual=False)
            self.assertEqual(elements['action',]['image'], f'button_{result}_disabled2')
            self.assertIsNone(elements['action',]['action'])
            self.assertEqual(elements['restart',]['action'], ('new_game', ()))
            for index in range(2):
                self.assertEqual(elements['laurels', index]['visible'], winner == index)
                self.assertEqual(elements['divider', index]['image'],
                                 'divider_active' if winner == index else 'divider_inactive')

    def test_resize_centers_board_and_stretches_only_composites(self):
        before, minimum = self.scene()
        after, new_minimum = self.scene(width=2200, height=1600)
        self.assertEqual(minimum, new_minimum)
        self.assertEqual(after['market', 1, 0]['x'] - before['market', 1, 0]['x'], 250)
        self.assertIsNone(after['market', 1, 0]['size'])
        self.assertEqual(after['background',]['size'], (2200, 1600))
        self.assertEqual(after['divider', 0]['size'][0], 2160)

    def test_piles_remain_centered_and_bottom_aligned_when_images_change(self):
        self.state.players[0].tokens = {RUBY: 4, GOLD: 2, DIAMOND: 4, SAPPHIRE: 2}
        for token, count in self.state.players[0].tokens.items():
            self.state.supply[token] -= count
        self.selection.returning = True
        before, _ = self.scene()
        self.selection.select_return_token(RUBY, self.state)
        after, _ = self.scene()
        for scene in (before, after):
            selected = scene.get(('selected-token', RUBY))
            if selected:
                height = self.sizes[selected['image']][1]
                self.assertEqual(selected['y'] + height / 2,
                                 scene['action',]['y'] + 210 / 2)
        # Changing a bottom-right aligned pile must retain its bottom-right edge.
        pile_before = before['player-token', 0, RUBY]
        pile_after = after['player-token', 0, RUBY]
        for axis, dimension in (('x', 0), ('y', 1)):
            self.assertEqual(pile_before[axis] + self.sizes[pile_before['image']][dimension],
                             pile_after[axis] + self.sizes[pile_after['image']][dimension])

    def test_reserved_overlay_has_same_action_and_selected_slot_stays_empty(self):
        cards = self.state.market[1][:3]
        self.state.players[0].reserved_cards = cards
        for card in cards:
            card.cost = {}
        self.selection.select_card(cards[1], self.state)
        elements, _ = self.scene()
        for slot in (0, 2):
            base = elements['player-card', 0, None, slot]
            overlay = elements['player-overlay', 0, slot]
            self.assertEqual(base['action'], overlay['action'])
            self.assertEqual(base['action'], ('select_card', (cards[slot],)))
            self.assertGreater(overlay['order'], base['order'])
        self.assertFalse(elements['player-card', 0, None, 1]['visible'])
        self.assertFalse(elements['player-overlay', 0, 1]['visible'])
        disabled, _ = self.scene(manual=False)
        self.assertIsNone(disabled['player-overlay', 0, 0]['action'])
