"""Run with SPLENDOR_GUI_TESTS=1 when Tk has window-server access."""
import os
import tkinter as tk
import unittest
from unittest.mock import patch

from ai import GreedyAI
from app.app import App
from app.assets import load_image
from game.constants import GOLD, RUBY, DIAMOND, SAPPHIRE
from game.initialize import create_initial_state


@unittest.skipUnless(os.environ.get('SPLENDOR_GUI_TESTS') == '1', 'Requires a GUI session')
class PersistentUITests(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.errors = []
        self.root.report_callback_exception = lambda kind, error, tb: self.errors.append(error)
        self.app = App(self.root, create_initial_state(), None)
        self.root.update()

    def tearDown(self):
        if self.root.winfo_exists():
            self.root.destroy()
        self.assertEqual(self.errors, [])

    def item(self, key):
        return self.app.renderer.items[key]

    def image(self, key):
        return self.app.renderer.descriptions[key]['image']

    def click(self, key, dx=None, dy=None):
        canvas = self.app.canvas
        x1, y1, x2, y2 = canvas.bbox(self.item(key))
        x, y = int((x1 + x2) / 2 if dx is None else x1 + dx), int((y1 + y2) / 2 if dy is None else y1 + dy)
        canvas.event_generate('<Motion>', x=x, y=y)
        canvas.event_generate('<Button-1>', x=x, y=y)
        self.root.update_idletasks()

    def test_one_canvas_and_only_images(self):
        self.assertEqual(self.root.winfo_children(), [self.app.canvas])
        self.assertEqual(self.app.canvas.winfo_children(), [])
        self.assertTrue(all(self.app.canvas.type(item) == 'image' for item in self.app.canvas.find_all()))

    def test_unchanged_render_does_not_touch_items_or_rebuild_images(self):
        app = self.app
        with patch.object(app.canvas, 'coords', wraps=app.canvas.coords) as coords, \
                patch.object(app.canvas, 'itemconfigure', wraps=app.canvas.itemconfigure) as configure, \
                patch.object(app.canvas, 'create_image', wraps=app.canvas.create_image) as create, \
                patch.object(app.canvas, 'tag_raise', wraps=app.canvas.tag_raise) as raise_item, \
                patch.object(app.renderer.background, 'resize') as background:
            app.render()
            coords.assert_not_called()
            configure.assert_not_called()
            create.assert_not_called()
            raise_item.assert_not_called()
            background.assert_not_called()

    def test_action_permissions_buy_reserve_pass_and_restart(self):
        app = self.app
        self.assertEqual(self.image(('action',)), 'button_pass_enabled2')
        self.click(('supply', RUBY))
        self.assertEqual(self.image(('action',)), 'button_take_disabled2')
        self.click(('action',))
        self.assertEqual(app.state.players[0].tokens, {})
        self.click(('supply', RUBY))
        self.click(('action',))
        self.assertEqual(app.state.players[0].tokens, {RUBY: 2})
        self.click(('action',))
        card = app.state.market[1][0]
        card.cost = {}
        app.refresh()
        self.click(('market-overlay', 1, 0))
        self.assertIs(app.selection.card, card)
        self.assertEqual(self.image(('action',)), 'button_buy_enabled2')
        self.click(('selected-overlay',))
        self.assertIsNone(app.selection.card)
        self.click(('market-overlay', 1, 0))
        self.click(('supply', GOLD))
        self.assertEqual(self.image(('action',)), 'button_reserve_enabled2')
        self.click(('action',))
        self.assertIn(card, app.state.players[0].reserved_cards)
        old_state, old_selection = app.state, app.selection
        self.click(('restart',))
        self.assertIsNot(app.state, old_state)
        self.assertIsNot(app.selection, old_selection)
        self.assertFalse(any(player.is_ai for player in app.state.players))

    def test_items_survive_turn_resize_restart_and_cached_images(self):
        app = self.app
        original = dict(app.renderer.items)
        app.select_token(RUBY)
        with patch('app.assets.tk.PhotoImage', side_effect=AssertionError('Reloaded image')):
            load_image(app.canvas, 'ruby')
            app.deselect_token(RUBY)
            app.select_token(RUBY)
        app.select_token(RUBY)
        app.perform_action()
        for width in (1900, 2207, 1800):
            self.root.geometry(f'{width}x1400')
            self.root.update()
        app.new_game()
        self.root.update()
        for key, item in original.items():
            self.assertEqual(app.renderer.items[key], item)
        self.assertEqual(app.canvas.itemcget(self.item(('selected-token', RUBY)), 'state'), 'hidden')

    def test_dynamic_card_pool_reuses_hidden_slots_and_updates_actions(self):
        app = self.app
        cards = app.state.market[1][:3]
        for card in cards:
            card.cost = {}
        player = app.state.players[0]
        player.reserved_cards = list(cards)
        app.refresh()
        slots = [self.item(('player-card', 0, None, i)) for i in range(3)]
        for index, card in enumerate(cards):
            self.click(('player-overlay', 0, index), dx=10, dy=100)
            self.assertIs(app.selection.card, card)
            self.assertEqual(app.canvas.itemcget(slots[index], 'state'), 'hidden')
            self.click(('selected-card',), dx=75, dy=150)
            self.assertIsNone(app.selection.card)
        player.reserved_cards.pop(0)
        app.refresh()
        self.assertEqual(self.item(('player-card', 0, None, 0)), slots[0])
        self.click(('player-overlay', 0, 0), dx=10, dy=100)
        self.assertIs(app.selection.card, cards[1])
        app.selection.clear()
        player.reserved_cards.clear()
        app.refresh()
        self.assertTrue(all(app.canvas.itemcget(item, 'state') == 'hidden' for item in slots))
        player.reserved_cards = list(cards)
        app.refresh()
        self.assertEqual(slots, [self.item(('player-card', 0, None, i)) for i in range(3)])

    def test_returns_select_owned_piles_and_require_exact_excess(self):
        app = self.app
        app.state.players[0].tokens = {RUBY: 4, GOLD: 2, DIAMOND: 4, SAPPHIRE: 2}
        for token, count in app.state.players[0].tokens.items():
            app.state.supply[token] -= count
        app.selection.returning = True
        app.refresh()
        supply = self.image(('supply', RUBY))
        self.click(('player-token', 0, RUBY))
        self.assertEqual(app.selection.tokens, {RUBY: 1})
        self.assertEqual(self.image(('action',)), 'button_return_disabled2')
        self.click(('player-token', 0, GOLD))
        self.assertEqual(self.image(('action',)), 'button_return_enabled2')
        self.assertEqual(self.image(('supply', RUBY)), supply)
        self.click(('selected-token', GOLD))
        self.assertEqual(app.selection.tokens, {RUBY: 1})
        self.click(('player-token', 0, GOLD))
        self.click(('action',))
        self.assertEqual(app.state.players[0].token_count, 10)
        self.assertEqual(app.state.turn.active_player, 1)

    def test_decks_results_and_restart_restore_visibility(self):
        app = self.app
        position = app.canvas.coords(self.item(('market', 1, 0)))
        app.state.decks[1].clear()
        app.state.market[1].clear()
        app.refresh()
        self.assertEqual(app.canvas.itemcget(self.item(('deck', 1)), 'state'), 'hidden')
        self.assertEqual(app.canvas.coords(self.item(('market', 1, 0))), position)
        for winner, result in ((0, 'win'), (1, 'loose'), (None, 'tie')):
            app.state.turn.finished = True
            app.state.turn.winner = winner
            app.refresh()
            self.assertEqual(self.image(('action',)), f'button_{result}_disabled2')
            for index in range(2):
                self.assertEqual(app.canvas.itemcget(self.item(('laurels', index)), 'state'),
                                 'normal' if index == winner else 'hidden')
            self.click(('action',))
            self.assertTrue(app.state.turn.finished)
            self.click(('restart',))
            self.assertFalse(app.state.turn.finished)
            self.assertEqual(app.canvas.itemcget(self.item(('deck', 1)), 'state'), 'normal')

    def test_background_dividers_and_native_images_resize(self):
        app = self.app
        for width in (1900, 2207):
            self.root.geometry(f'{width}x1400')
            self.root.update()
            bg = app.renderer.background
            self.assertEqual(bg.size, (app.canvas.winfo_width(), app.canvas.winfo_height()))
            self.assertEqual(bg.image.get(10, 10), bg.fragments[0, 0].get(10, 10))
            for index in (0, 1):
                name = self.image(('divider', index))
                image = app.renderer.images[name]
                left = load_image(app.canvas, name + '_left')
                right = load_image(app.canvas, name + '_right')
                middle = load_image(app.canvas, name + '_middle')
                self.assertEqual(image.width(), width - 40)
                self.assertEqual(image.get(30, 26), left.get(30, 26))
                self.assertEqual(image.get(image.width() - 30, 26), right.get(right.width() - 30, 26))
                self.assertEqual(image.get(300, 26), middle.get((300-left.width()) % middle.width(), 26))
            bounds = app.canvas.bbox(self.item(('market', 1, 0)))
            self.assertEqual((bounds[2] - bounds[0], bounds[3] - bounds[1]), (150, 210))
            self.assertEqual(app.canvas.find_all()[0], self.item(('background',)))

    def test_ai_callbacks_survive_render_and_cancel_on_restart_and_destroy(self):
        app = self.app
        app.strategy = GreedyAI()
        app.state.players[1].is_ai = True
        app.state.turn.active_player = 1
        app.refresh()
        pending = app.pending_ai
        app.render()
        self.assertEqual(app.pending_ai, pending)
        self.root.after_cancel(pending)
        app.perform_ai_selection()
        pending = app.pending_ai
        app.render()
        self.assertEqual(app.pending_ai, pending)
        app.new_game()
        self.assertNotIn(pending, self.root.tk.call('after', 'info'))
        app.state.turn.active_player = 1
        app.refresh()
        pending = app.pending_ai
        app.on_destroy(type('Event', (), {'widget': self.root})())
        self.assertIsNone(app.pending_ai)
        self.assertNotIn(pending, self.root.tk.call('after', 'info'))
