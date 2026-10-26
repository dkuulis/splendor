"""Run with SPLENDOR_GUI_TESTS=1 when Tk has window-server access."""
import os
import tkinter as tk
import unittest
from unittest.mock import patch

from app.app import App
from app.assets import load_image
from game.constants import RUBY, GOLD
from game.initialize import create_initial_state


@unittest.skipUnless(os.environ.get('SPLENDOR_GUI_TESTS') == '1', 'Requires a GUI session')
class PersistentUITests(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.callback_errors = []
        self.root.report_callback_exception = lambda kind, error, traceback: self.callback_errors.append(error)
        self.app = App(self.root, create_initial_state())
        self.app.control.set('Manual')
        self.app.change_control()
        self.root.update()

    def tearDown(self):
        self.root.destroy()
        self.assertEqual(self.callback_errors, [])

    def widgets(self, widget):
        return [widget] + [child for item in widget.winfo_children() for child in self.widgets(item)]

    def test_widgets_and_canvas_items_survive_selection_turns_and_reset(self):
        app = self.app
        widgets = self.widgets(app.field)
        selection_items = app.selection.tokens.find_all()
        market_items = [panel.find_all() for _, panel in app.market.cards]
        app.select_token(RUBY)
        app.deselect_token(RUBY)
        with patch('app.assets.tk.PhotoImage', side_effect=AssertionError('Reloaded cached image')):
            load_image(app.selection, 'ruby')
            app.select_token(RUBY)
            app.deselect_token(RUBY)
        app.select_token(RUBY)
        app.selection.go_button.invoke()
        self.assertEqual(app.state.players[0].tokens[RUBY], 1)
        app.selection.go_button.invoke()  # Computer passes in manual mode.
        card = app.state.market[1][0]
        for token, count in card.cost.items():
            needed = max(0, count - app.state.current_player.tokens.get(token, 0))
            app.state.current_player.tokens[token] = app.state.current_player.tokens.get(token, 0) + needed
            app.state.supply[token] -= needed
        app.refresh()
        panel = app.market.slots[1][0]
        panel.select(None)
        self.root.update()
        self.assertIs(app.state.selected_card, card)
        self.assertFalse(panel.winfo_ismapped())
        app.selection.card.select(None)
        self.assertIsNone(app.state.selected_card)
        panel.select(None)
        app.selection.go_button.invoke()
        self.assertIn(card, app.state.players[0].cards[card.token])
        replacement = app.state.market[1][0]
        self.assertIs(panel.card, replacement)
        app.state.decks[1].clear()
        app.state.market[1].clear()
        app.refresh()
        self.root.update()
        self.assertTrue(all(not slot.winfo_ismapped() for slot in app.market.slots[1]))
        app.new_game()
        self.root.update()
        self.assertEqual(widgets, self.widgets(app.field))
        self.assertEqual(selection_items, app.selection.tokens.find_all())
        self.assertEqual(market_items, [panel.find_all() for _, panel in app.market.cards])
        self.assertIs(app.selection.state, app.state)
        self.assertIs(app.supply.available_tokens, app.state.supply)
        self.assertIs(app.scores.players, app.state.players)
        self.assertTrue(all(slot.winfo_ismapped() for slot in app.market.slots[1]))

    def test_control_changes_disable_callbacks_and_cancel_ai(self):
        app = self.app
        app.perform_action()
        app.control.set('Greedy AI')
        app.change_control()
        self.assertIsNotNone(app.pending_ai)
        app.supply.pick(RUBY)
        self.assertEqual(app.state.selected_tokens, {})
        self.assertFalse(app.selection.can_go)
        app.control.set('Manual')
        app.change_control()
        self.assertIsNone(app.pending_ai)
        app.supply.pick(RUBY)
        self.assertEqual(app.state.selected_tokens, {RUBY: 1})
        app.control.set('Greedy AI')
        app.change_control()
        app.new_game()
        self.assertIsNone(app.pending_ai)
        app.perform_action()
        app.cancel_ai()
        app.run_ai()
        self.assertEqual(app.state.turn.active_player, 0)

    def test_nobles_follow_state_and_are_centered_left_of_supply(self):
        app = self.app
        panel = app.nobles
        slots = list(panel.slots)
        self.assertEqual(len(slots), 3)
        self.assertIs(panel.master, app.supply.master)
        for neighbor in (app.supply, app.selection):
            self.assertLess(panel.winfo_rootx() + panel.winfo_width(), neighbor.winfo_rootx())
        self.assertAlmostEqual(panel.winfo_y() + panel.winfo_height() / 2,
                               panel.master.winfo_height() / 2, delta=1)
        top_card = app.market.slots[3][0]
        next_card = app.market.slots[2][0]
        card_gap = next_card.winfo_rooty() - top_card.winfo_rooty() - top_card.winfo_height()
        self.assertEqual(slots[1].winfo_rooty() - slots[0].winfo_rooty()
                         - slots[0].winfo_height(), card_gap)
        for tile, noble in zip(slots, app.state.nobles):
            self.assertEqual(tile.itemcget(1, 'image'), str(load_image(tile, noble.id)))
            self.assertEqual(tile.winfo_width(), 150)
            self.assertEqual(tile.winfo_height(), 150)
        app.state.nobles.pop(0)
        app.refresh()
        self.root.update()
        self.assertEqual(slots[0].itemcget(1, 'image'),
                         str(load_image(slots[0], app.state.nobles[0].id)))
        self.assertFalse(slots[-1].winfo_ismapped())
        self.assertAlmostEqual(panel.winfo_y() + panel.winfo_height() / 2,
                               panel.master.winfo_height() / 2, delta=1)
        app.state.nobles.clear()
        app.refresh()
        self.root.update()
        self.assertTrue(all(not tile.winfo_ismapped() for tile in slots))
        app.new_game()
        self.root.update()
        self.assertEqual(slots, panel.slots)
        self.assertIs(panel.nobles, app.state.nobles)
        self.assertTrue(all(tile.winfo_ismapped() for tile in slots))

    def test_player_nobles_and_gold_share_leftmost_column(self):
        app = self.app
        nobles = app.state.nobles[:2]
        card = app.state.market[1][0]
        for player, panel in zip(app.state.players, (app.player, app.computer)):
            column = panel.columns[GOLD]
            self.assertFalse(column.winfo_ismapped())
            player.tokens[GOLD] = 5
            app.refresh()
            self.root.update()
            self.assertTrue(column.winfo_ismapped())
            self.assertEqual(len(column.token_items), 5)
            player.nobles = list(nobles)
            player.add_card(card)
            app.refresh()
            self.root.update()
            gem_column = panel.columns[card.token]
            self.assertLess(column.winfo_rootx() + column.winfo_width(), gem_column.winfo_rootx())
            self.assertEqual(column.stack.winfo_height(), 150)
            for item, noble in zip(column.card_items, nobles):
                self.assertEqual(column.stack.itemcget(item, 'image'), str(load_image(column, noble.id)))
            self.assertEqual(column.stack.coords(column.card_items[1])[0]
                             - column.stack.coords(column.card_items[0])[0], 30)
            for item in column.token_items:
                self.assertEqual(column.stack.itemcget(item, 'image'), str(load_image(column, 'gold')))
                self.assertEqual(column.stack.itemcget(item, 'state'), 'normal')
            self.assertEqual(list(column.stack.find_all()), column.card_items + column.token_items)
            player.tokens.clear()
            app.refresh()
            self.root.update()
            self.assertTrue(column.winfo_ismapped())
            self.assertTrue(all(column.stack.itemcget(item, 'state') == 'hidden'
                                for item in column.token_items))
        app.new_game()
        self.root.update()
        self.assertFalse(app.player.columns[GOLD].winfo_ismapped())
        self.assertFalse(app.computer.columns[GOLD].winfo_ismapped())

    def test_log_scroll_and_label_reuse(self):
        app = self.app
        app.state.log.extend(f'Message {index}' for index in range(100))
        app.log.refresh()
        self.root.update()
        self.assertGreaterEqual(app.log.canvas.yview()[1], 0.999)
        labels = list(app.log.labels)
        app.log.canvas.yview_moveto(0.3)
        top = app.log.canvas.canvasy(0)
        app.state.log.append('New entry')
        app.log.refresh()
        self.root.update()
        self.assertAlmostEqual(app.log.canvas.canvasy(0), top, delta=1)
        self.assertEqual(labels, app.log.labels[:-1])
        app.new_game()
        self.root.update()
        self.assertEqual(labels, app.log.labels[:-1])
        self.assertEqual(len(app.log.displayed_messages), 1)
        self.assertTrue(all(not label.winfo_ismapped() for label in app.log.labels[1:]))
        app.perform_action()
        self.root.update()
        self.assertTrue(app.log.labels[1].winfo_ismapped())
        self.assertEqual(app.log.labels[1].cget('text'), app.state.log[1])
