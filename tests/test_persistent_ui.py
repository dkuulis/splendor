"""Run with SPLENDOR_GUI_TESTS=1 when Tk has window-server access."""
import os
import tkinter as tk
from tkinter import ttk
import unittest
from unittest.mock import patch

from ai import GreedyAI
from app.app import App
from app.assets import load_image
from game.constants import RUBY, GOLD
from game.initialize import create_initial_state


@unittest.skipUnless(os.environ.get('SPLENDOR_GUI_TESTS') == '1', 'Requires a GUI session')
class PersistentUITests(unittest.TestCase):
    def setUp(self):
        self.create_app(None)

    def create_app(self, strategy):
        self.root = tk.Tk()
        self.callback_errors = []
        self.root.report_callback_exception = lambda kind, error, traceback: self.callback_errors.append(error)
        self.app = App(self.root, create_initial_state(), strategy)
        self.root.update()

    def tearDown(self):
        self.root.destroy()
        self.assertEqual(self.callback_errors, [])

    @property
    def action_button(self):
        return self.app.selection.action_button

    def widgets(self, widget):
        return [widget] + [child for item in widget.winfo_children() for child in self.widgets(item)]

    def test_action_buttons_fit_and_keep_positions_across_selection_and_restart(self):
        app = self.app
        panel = app.selection
        action = panel.action_button
        restart = panel.restart_button
        buttons = (action, restart)
        self.assertEqual([child for child in panel.actions.winfo_children()
                          if isinstance(child, ttk.Button)], list(buttons))
        positions = []
        for button in buttons:
            self.assertTrue(button.winfo_ismapped())
            self.assertEqual((button.winfo_width(), button.winfo_height()), (140, 42))
            self.assertGreaterEqual(button.winfo_y(), 0)
            self.assertLessEqual(button.winfo_y() + button.winfo_height(), 210)
            positions.append((button.winfo_x(), button.winfo_y()))
        self.assertLess(action.winfo_y() + action.winfo_height(), restart.winfo_y())
        self.assertEqual(panel.actions.winfo_height(), 210)
        self.assertFalse(action.instate(['disabled']))
        self.assertEqual(action.cget('text'), 'Pass')
        self.assertEqual(action.cget('image')[0], str(load_image(panel, 'button_pass_enabled')))
        app.select_token(RUBY)
        self.assertEqual(action.cget('text'), 'Take')
        self.assertEqual(action.cget('image')[0], str(load_image(panel, 'button_take_enabled')))
        action.invoke()
        self.assertEqual(app.state.players[0].tokens, {RUBY: 1})
        self.assertEqual(action.cget('text'), 'Pass')
        action.invoke()
        self.assertEqual(app.state.players[1].tokens, {})
        self.assertEqual(app.state.turn.active_player, 0)
        self.assertEqual(app.state.turn.consecutive_passes, 1)
        card = app.state.market[1][0]
        card.cost = {RUBY: 1}
        app.select_card(card)
        self.assertEqual(action.cget('text'), 'Buy')
        self.assertEqual(action.cget('image')[0], str(load_image(panel, 'button_buy_enabled')))
        self.assertFalse(action.instate(['disabled']))
        app.select_token(GOLD)
        self.assertEqual(action.cget('text'), 'Reserve')
        self.assertEqual(action.cget('image')[0], str(load_image(panel, 'button_reserve_enabled')))
        self.assertFalse(action.instate(['disabled']))
        self.assertIs(panel.action_button, action)
        self.assertEqual(positions, [(button.winfo_x(), button.winfo_y()) for button in buttons])
        app.state.turn.finished = True
        app.refresh()
        self.assertTrue(action.instate(['disabled']))
        self.assertFalse(restart.instate(['disabled']))
        old_state = app.state
        restart.invoke()
        self.root.update()
        self.assertIsNot(app.state, old_state)
        self.assertFalse(app.state.turn.finished)
        self.assertIs(panel.action_button, action)
        self.assertEqual(action.cget('text'), 'Pass')
        self.assertEqual(positions, [(button.winfo_x(), button.winfo_y()) for button in buttons])

    def test_gold_first_selects_and_toggles_a_reservation(self):
        app = self.app
        card = app.state.market[1][0]
        app.select_token(GOLD)
        self.assertEqual(app.state.selection.action_kind, 'reserve')
        self.assertTrue(self.action_button.instate(['disabled']))
        app.select_card(card)
        self.assertIs(app.state.selection.card, card)
        self.assertEqual(app.state.selection.tokens, {GOLD: 1})
        self.assertFalse(self.action_button.instate(['disabled']))
        app.selection.card.select(None)
        self.assertEqual(app.state.selection.action_kind, 'pass')
        self.assertIsNone(app.state.selection.card)
        self.assertEqual(app.state.selection.tokens, {})
        app.select_token(GOLD)
        app.select_card(card)
        self.action_button.invoke()
        self.assertIn(card, app.state.players[0].reserved_cards)
        self.assertEqual(app.state.players[0].tokens, {GOLD: 1})

    def test_dividers_tile_across_resizes_and_switch_with_turns(self):
        app = self.app
        dividers = (app.player_divider, app.computer_divider)
        items = [divider.find_all() for divider in dividers]
        for width in (1900, 2207, 1800):
            self.root.geometry(f"{width}x1400")
            self.root.update()
            for index, divider in enumerate(dividers):
                self.assertEqual(divider.winfo_width(),
                                 app.field.winfo_width() - 2 * divider.winfo_x())
                self.assertEqual(divider.winfo_height(), divider.height)
                self.assertEqual(divider.find_all(), items[index])
                active = index == app.state.turn.active_player
                image = divider.images[active]
                self.assertEqual(divider.itemcget(divider.divider, 'image'), str(image))
                self.assertEqual(divider.itemcget(divider.plaque, 'image'),
                                 str(divider.plaque_images[active]))
                self.assertEqual(image.width(), divider.winfo_width())
                score_bounds = divider.bbox(divider.points)
                plaque_bounds = divider.bbox(divider.plaque)
                self.assertGreater(plaque_bounds[0], 30)
                self.assertLess(plaque_bounds[0], score_bounds[0])
                self.assertGreater(plaque_bounds[2], score_bounds[2])
                self.assertLess(plaque_bounds[1], score_bounds[1])
                self.assertGreater(plaque_bounds[3], score_bounds[3])
                self.assertLess(divider.find_all().index(divider.divider),
                                divider.find_all().index(divider.plaque))
                self.assertLess(divider.find_all().index(divider.plaque),
                                divider.find_all().index(divider.points))
                self.assertGreaterEqual(divider.bbox(divider.points)[1], 0)
                self.assertLessEqual(divider.bbox(divider.points)[3], divider.height)
                left, middle, right = divider.tiles[active]
                self.assertEqual(image.get(30, 26), left.get(30, 26))
                self.assertEqual(image.get(image.width() - 30, 26),
                                 right.get(right.width() - 30, 26))
                for x in range(left.width(), image.width() - right.width()):
                    self.assertEqual(image.get(x, 26),
                                     middle.get((x - left.width()) % middle.width(), 26))
            app.select_token(RUBY)
            app.perform_action()
            self.root.update()
        app.new_game()
        self.assertEqual(app.player_divider.itemcget(app.player_divider.divider, 'image'),
                         str(app.player_divider.images[True]))
        self.assertEqual(app.player_divider.itemcget(app.player_divider.plaque, 'image'),
                         str(app.player_divider.plaque_images[True]))
        self.assertEqual(app.computer_divider.itemcget(app.computer_divider.plaque, 'image'),
                         str(app.computer_divider.plaque_images[False]))

    def test_winner_laurels_and_highlight_preserve_height_and_reset(self):
        app = self.app
        dividers = (app.player_divider, app.computer_divider)
        heights = [divider.winfo_height() for divider in dividers]
        items = [divider.find_all() for divider in dividers]
        for winner in (0, 1, None):
            with self.subTest(winner=winner):
                app.new_game()
                if winner is not None:
                    app.state.players[winner].nobles.append(app.state.nobles.pop())
                app.perform_action()
                app.perform_action()
                self.assertTrue(app.state.turn.finished)
                self.assertEqual(app.state.turn.winner, winner)
                app.refresh()
                self.root.update()
                for index, divider in enumerate(dividers):
                    highlighted = index == winner
                    self.assertEqual(divider.itemcget(divider.divider, 'image'),
                                     str(divider.images[highlighted]))
                    self.assertEqual(divider.itemcget(divider.plaque, 'image'),
                                     str(divider.plaque_images[highlighted]))
                    self.assertEqual(divider.itemcget(divider.laurels, 'state'),
                                     'normal' if highlighted else 'hidden')
                    self.assertEqual(divider.winfo_height(), heights[index])
                    self.assertEqual(divider.find_all(), items[index])
                    if highlighted:
                        bounds = divider.bbox(divider.laurels)
                        self.assertGreaterEqual(bounds[1], 0)
                        self.assertLessEqual(bounds[3], heights[index])
        app.new_game()
        for index, divider in enumerate(dividers):
            self.assertEqual(divider.itemcget(divider.laurels, 'state'), 'hidden')
            self.assertEqual(divider.itemcget(divider.divider, 'image'),
                             str(divider.images[index == 0]))

    def test_divider_points_follow_cards_nobles_and_restart(self):
        app = self.app
        player, computer = app.state.players
        for owner, card in zip((player, computer), app.state.market[3][:2]):
            owner.add_card(card)
        player.nobles.append(app.state.nobles.pop())
        app.refresh()
        self.root.update()
        for owner, divider in ((player, app.player_divider), (computer, app.computer_divider)):
            self.assertEqual(divider.itemcget(divider.points, 'text'), str(owner.points))
            self.assertEqual([divider.itemcget(item, 'text') for item in divider.find_all()
                              if divider.type(item) == 'text'], [str(owner.points)])
        app.new_game()
        for divider in (app.player_divider, app.computer_divider):
            self.assertEqual(divider.itemcget(divider.points, 'text'), '0')

    def test_background_stays_aligned_after_resize_and_new_game(self):
        background = self.app.background
        for width, height in ((1900, 1300), (2560, 1600), (2100, 1450)):
            self.root.geometry(f"{width}x{height}")
            self.root.update()
            self.assertEqual(background.size,
                             (self.root.winfo_width(), self.root.winfo_height()))
            for frame in (self.app.field, self.app.player.panel, self.app.supply):
                surface, _, _ = background.surfaces[frame]
                self.assertEqual((surface.winfo_x(), surface.winfo_y()), (0, 0))
                self.assertEqual((surface.winfo_width(), surface.winfo_height()),
                                 (frame.winfo_width(), frame.winfo_height()))
            for widget in (self.app.field, self.app.player.panel,
                           self.app.supply.cells[RUBY], self.app.selection.tokens,
                           self.app.player_divider, self.app.computer_divider):
                surface, item, image = background.surfaces[widget]
                x = surface.winfo_rootx() - self.root.winfo_rootx()
                y = surface.winfo_rooty() - self.root.winfo_rooty()
                self.assertEqual(image.get(10, 10), background.image.get(x + 10, y + 10))
                if item is not None:
                    self.assertEqual(surface.find_all()[0], item)
            # Every corner retains its original pixels and proportions even
            # when the middle of the window is stretched in either direction.
            w, h = background.size
            for dx, dy in ((10, 10), (80, 150), (230, 30), (30, 230), (259, 259)):
                for column, x in ((0, dx), (2, w - 1 - dx)):
                    for row, y in ((0, dy), (2, h - 1 - dy)):
                        corner = background.fragments[row, column]
                        sx = dx if column == 0 else corner.width() - 1 - dx
                        sy = dy if row == 0 else corner.height() - 1 - dy
                        self.assertEqual(background.image.get(x, y), corner.get(sx, sy))
            center = background.fragments[1, 1]
            self.assertEqual(background.image.get(w // 2, h // 2),
                             center.get(center.width() // 2, center.height() // 2))
            self.assertNotIn("background", self.root._splendor_images)
        surfaces = dict(background.surfaces)
        self.app.new_game()
        self.root.update()
        self.assertEqual(background.surfaces, surfaces)

    def test_widgets_and_canvas_items_survive_selection_turns_and_reset(self):
        app = self.app
        widgets = self.widgets(app.field)
        selection_items = app.selection.tokens.find_all()
        market_items = [panel.find_all() for panels in app.market.slots.values() for panel in panels]
        app.select_token(RUBY)
        app.deselect_token(RUBY)
        with patch('app.assets.tk.PhotoImage', side_effect=AssertionError('Reloaded cached image')):
            load_image(app.selection, 'ruby')
            app.select_token(RUBY)
            app.deselect_token(RUBY)
        app.select_token(RUBY)
        self.action_button.invoke()
        self.assertEqual(app.state.players[0].tokens[RUBY], 1)
        self.action_button.invoke()  # Computer passes in manual mode.
        card = app.state.market[1][0]
        for token, count in card.cost.items():
            needed = max(0, count - app.state.current_player.tokens.get(token, 0))
            app.state.current_player.tokens[token] = app.state.current_player.tokens.get(token, 0) + needed
            app.state.supply[token] -= needed
        app.refresh()
        panel = app.market.slots[1][0]
        panel.select(None)
        self.root.update()
        self.assertIs(app.state.selection.card, card)
        self.assertFalse(panel.winfo_ismapped())
        app.selection.card.select(None)
        self.assertIsNone(app.state.selection.card)
        panel.select(None)
        self.action_button.invoke()
        self.assertIn(card, app.state.players[0].cards[card.token])
        replacement = app.state.market[1][0]
        self.assertIs(panel.card, replacement)
        app.state.decks[1].clear()
        app.state.market[1].clear()
        app.refresh()
        self.root.update()
        self.assertTrue(all(not slot.winfo_ismapped() for slot in app.market.slots[1]))
        app.select_token(RUBY)
        previous_selection = app.state.selection
        app.new_game()
        self.root.update()
        self.assertIsNot(app.state.selection, previous_selection)
        self.assertIsNone(app.state.selection.card)
        self.assertEqual(app.state.selection.tokens, {})
        self.assertEqual(widgets, self.widgets(app.field))
        self.assertEqual(selection_items, app.selection.tokens.find_all())
        self.assertEqual(market_items, [panel.find_all() for panels in app.market.slots.values() for panel in panels])
        self.assertIs(app.selection.state, app.state)
        self.assertEqual(app.supply.counts, app.state.supply)
        self.assertEqual([divider.itemcget(divider.points, 'text')
                          for divider in (app.player_divider, app.computer_divider)], ['0', '0'])
        self.assertTrue(all(slot.winfo_ismapped() for slot in app.market.slots[1]))

    def test_ai_blocks_manual_actions_and_new_game_cancels_callback(self):
        self.root.destroy()
        strategy = GreedyAI()
        self.create_app(strategy)
        app = self.app
        app.perform_action()
        self.assertIsNotNone(app.pending_ai)
        app.supply.pick(RUBY)
        self.assertEqual(app.state.selection.tokens, {})
        self.assertFalse(app.selection.can_go)
        app.market.slots[1][0].select(None)
        self.assertIsNone(app.state.selection.card)
        pending = app.pending_ai
        app.selection.restart_button.invoke()
        self.assertIsNone(app.pending_ai)
        self.assertNotIn(pending, self.root.tk.call('after', 'info'))
        self.assertIs(app.strategy, strategy)
        app.perform_action()
        app.cancel_ai()
        app.run_ai()
        self.assertEqual(app.state.turn.active_player, 0)

    def test_unaffordable_card_selects_reserve_and_can_switch_back_to_buy(self):
        app = self.app
        panel = app.market.slots[1][0]
        card = panel.card
        card.cost = {RUBY: 2}
        app.refresh()
        panel.event_generate('<Button-1>')
        self.root.update()
        self.assertIs(app.state.selection.card, card)
        self.assertFalse(panel.winfo_ismapped())
        self.assertTrue(app.selection.card.winfo_ismapped())
        self.assertEqual(app.state.selection.tokens, {GOLD: 1})
        self.assertEqual(self.action_button.cget('text'), 'Reserve')
        self.assertFalse(self.action_button.instate(['disabled']))
        overlay = app.selection.disabled_overlay
        self.assertEqual(app.selection.card.itemcget(overlay, 'image'),
                         str(load_image(app.selection, 'disabled')))
        self.assertEqual(app.selection.card.itemcget(overlay, 'state'), 'normal')
        self.assertEqual(app.state.turn.active_player, 0)
        self.assertIn(card, app.state.market[1])
        app.selection.card.event_generate('<Button-1>')
        self.root.update()
        self.assertIsNone(app.state.selection.card)
        self.assertTrue(panel.winfo_ismapped())
        panel.event_generate('<Button-1>')
        app.deselect_token(GOLD)
        self.assertEqual(self.action_button.cget('text'), 'Buy')
        self.assertTrue(self.action_button.instate(['disabled']))
        app.state.current_player.tokens[RUBY] = 2
        app.state.supply[RUBY] -= 2
        app.refresh()
        self.assertFalse(self.action_button.instate(['disabled']))
        self.assertEqual(app.selection.card.itemcget(overlay, 'state'), 'hidden')
        self.action_button.invoke()
        self.assertIn(card, app.state.players[0].cards[card.token])
        self.assertEqual(app.state.players[0].tokens, {})
        self.assertEqual(app.state.turn.active_player, 1)

    def test_owned_gold_enables_buy_and_clears_disabled_overlay(self):
        app = self.app
        card = app.state.market[1][0]
        card.cost = {RUBY: 2}
        app.select_card(card)
        self.assertEqual(self.action_button.cget('text'), 'Reserve')
        app.deselect_token(GOLD)
        self.assertTrue(self.action_button.instate(['disabled']))
        app.state.current_player.tokens[GOLD] = 2
        app.state.supply[GOLD] -= 2
        app.refresh()
        self.assertEqual(self.action_button.cget('text'), 'Buy')
        self.assertFalse(self.action_button.instate(['disabled']))
        self.assertEqual(app.selection.card.itemcget(app.selection.disabled_overlay, 'state'), 'hidden')
        self.action_button.invoke()
        self.assertIn(card, app.state.players[0].cards[card.token])
        self.assertEqual(app.state.players[0].tokens, {})

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
            self.assertEqual(column.stack.itemcget(column.token_item, 'image'),
                             str(load_image(column, 'gold5')))
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
            self.assertEqual(column.stack.itemcget(column.token_item, 'state'), 'normal')
            self.assertEqual(list(column.stack.find_withtag("!background")),
                             column.card_items + [column.token_item])
            self.assertEqual(column.stack.bbox(column.token_item)[2:],
                             (column.stack.winfo_width(), column.height))
            self.assertEqual(column.stack.bbox(column.token_item)[2]
                             - column.stack.bbox(column.card_items[-1])[2], 20)
            player.tokens.clear()
            app.refresh()
            self.root.update()
            self.assertTrue(column.winfo_ismapped())
            self.assertEqual(column.stack.itemcget(column.token_item, 'state'), 'hidden')
            gem_item = gem_column.token_item
            for count in (7, 2, 1, 0):
                player.tokens[card.token] = count
                app.refresh()
                self.root.update()
                self.assertEqual(gem_column.token_item, gem_item)
                if count:
                    name = card.token.lower() + (str(count) if count > 1 else '')
                    self.assertEqual(gem_column.stack.itemcget(gem_item, 'image'),
                                     str(load_image(gem_column, name)))
                    self.assertEqual(gem_column.stack.bbox(gem_item)[2:],
                                     (gem_column.stack.winfo_width(), gem_column.height))
                else:
                    self.assertEqual(gem_column.stack.itemcget(gem_item, 'state'), 'hidden')
        app.new_game()
        self.root.update()
        self.assertFalse(app.player.columns[GOLD].winfo_ismapped())
        self.assertFalse(app.computer.columns[GOLD].winfo_ismapped())

    def test_gold_can_be_selected_but_blocks_collection(self):
        app = self.app
        cell = app.supply.cells[GOLD]
        x, y = cell.coords('gem')
        cell.event_generate('<Motion>', x=int(x), y=int(y))
        cell.event_generate('<Button-1>', x=int(x), y=int(y))
        self.root.update()
        self.assertEqual(app.state.selection.tokens, {GOLD: 1})
        self.assertEqual(app.selection.tokens.itemcget(app.selection.items[GOLD], 'state'), 'normal')
        self.assertTrue(self.action_button.instate(['disabled']))
        app.select_token(RUBY)
        self.assertEqual(app.state.selection.tokens, {RUBY: 1})
        self.assertEqual(app.selection.tokens.itemcget(app.selection.items[GOLD], 'state'), 'hidden')
        self.assertFalse(self.action_button.instate(['disabled']))
        app.select_token(GOLD)
        self.assertEqual(app.state.selection.tokens, {GOLD: 1})
        self.assertEqual(app.selection.tokens.itemcget(app.selection.items[RUBY], 'state'), 'hidden')
        self.assertTrue(self.action_button.instate(['disabled']))
        self.action_button.invoke()
        self.assertEqual(app.state.players[0].tokens, {})
        self.assertEqual(app.state.turn.active_player, 0)
        x, y = app.selection.tokens.coords(app.selection.items[GOLD])
        app.selection.tokens.event_generate('<Motion>', x=int(x), y=int(y))
        app.selection.tokens.event_generate('<Button-1>', x=int(x), y=int(y))
        self.root.update()
        self.assertEqual(app.state.selection.tokens, {})
        self.assertFalse(self.action_button.instate(['disabled']))
        app.select_token(RUBY)
        self.action_button.invoke()
        self.assertEqual(app.state.players[0].tokens, {RUBY: 1})

    def test_gold_and_selected_card_are_visible_together(self):
        app = self.app
        card = app.state.market[1][0]
        card.cost = {}
        app.select_card(card)
        app.supply.pick(GOLD)
        self.root.update()
        self.assertIs(app.state.selection.card, card)
        self.assertFalse(app.market.slots[1][0].winfo_ismapped())
        self.assertTrue(app.selection.card.winfo_ismapped())
        self.assertTrue(app.selection.tokens.winfo_ismapped())
        self.assertLess(app.selection.tokens.winfo_rootx() + app.selection.tokens.winfo_width(),
                        app.selection.card.winfo_rootx())
        left = app.selection.tokens.winfo_rootx()
        right = app.selection.card.winfo_rootx() + app.selection.card.winfo_width()
        x, y, width, height = app.selection.grid_bbox(0, 0)
        self.assertAlmostEqual((left + right) / 2,
                               app.selection.winfo_rootx() + x + width / 2, delta=1)
        self.assertAlmostEqual(app.selection.tokens.winfo_rooty() + 30,
                               app.selection.card.winfo_rooty() + app.selection.card.winfo_height() / 2,
                               delta=1)
        self.assertEqual(self.action_button.cget('text'), 'Reserve')
        self.assertFalse(self.action_button.instate(['disabled']))
        app.selection.deselect(GOLD)
        self.root.update()
        self.assertIs(app.state.selection.card, card)
        self.assertFalse(app.selection.tokens.winfo_ismapped())
        self.assertAlmostEqual(app.selection.card.winfo_rootx() + app.selection.card.winfo_width() / 2,
                               app.selection.winfo_rootx() + x + width / 2, delta=1)
        self.assertFalse(self.action_button.instate(['disabled']))
        app.select_token(GOLD)
        self.action_button.invoke()
        self.root.update()
        self.assertIn(card, app.state.players[0].reserved_cards)
        self.assertEqual(app.state.players[0].tokens[GOLD], 1)
        self.assertTrue(app.player.reserved.winfo_ismapped())
        self.assertEqual(app.state.turn.active_player, 1)

    def test_reserve_button_obeys_token_and_reservation_limits(self):
        app = self.app
        card = app.state.market[1][0]
        app.select_card(card)
        app.select_token(GOLD)
        player = app.state.current_player
        for limit in ('tokens', 'reservations'):
            with self.subTest(limit=limit):
                if limit == 'tokens':
                    player.tokens = {RUBY: 7, GOLD: 3}
                else:
                    player.reserved_cards = app.state.market[2][:3]
                app.refresh()
                self.assertEqual(self.action_button.cget('text'), 'Reserve')
                self.assertTrue(self.action_button.instate(['disabled']))
                self.action_button.invoke()
                self.assertIs(app.state.selection.card, card)
                self.assertEqual(app.state.turn.active_player, 0)
                player.tokens.clear()
                player.reserved_cards.clear()
        app.refresh()
        self.assertFalse(self.action_button.instate(['disabled']))

    def test_reserved_stack_selects_each_card_and_buys_without_market_refill(self):
        app = self.app
        player = app.state.current_player
        cards = app.state.market[1][:3]
        del app.state.market[1][:3]
        player.reserved_cards.extend(cards)
        for card in cards:
            card.cost = {RUBY: 1}
        player.tokens = {GOLD: 1}
        app.state.supply[GOLD] -= 1
        other = app.state.market[2].pop()
        app.state.players[1].reserved_cards.append(other)
        app.refresh()
        self.root.update()
        stack = app.computer.reserved.stack
        stack.event_generate('<Motion>', x=75, y=100)
        stack.event_generate('<Button-1>', x=75, y=100)
        self.assertIsNone(app.state.selection.card)
        stack = app.player.reserved.stack
        for index, card in enumerate(cards):
            x, y = stack.coords(app.player.reserved.card_items[index])
            stack.event_generate('<Motion>', x=int(x) + 10, y=int(y) + 100)
            stack.event_generate('<Button-1>', x=int(x) + 10, y=int(y) + 100)
            self.assertIs(app.state.selection.card, card)
            self.assertEqual(self.action_button.cget('text'), 'Buy')
            self.assertFalse(self.action_button.instate(['disabled']))
            for slot, item in enumerate(app.player.reserved.card_items):
                expected = 'hidden' if slot == index else 'normal'
                self.assertEqual(stack.itemcget(item, 'state'), expected)
                self.assertEqual(stack.itemcget(app.player.reserved.overlay_items[slot], 'state'), expected)
            app.refresh()
            self.assertEqual(stack.itemcget(app.player.reserved.card_items[index], 'state'), 'hidden')
            app.selection.card.select(None)
            self.assertIsNone(app.state.selection.card)
            self.assertEqual(stack.itemcget(app.player.reserved.card_items[index], 'state'), 'normal')
            app.select_card(card)
            app.select_token(GOLD)
            self.assertEqual(app.state.selection.tokens, {})
        market = {tier: list(row) for tier, row in app.state.market.items()}
        decks = {tier: list(row) for tier, row in app.state.decks.items()}
        self.action_button.invoke()
        self.assertEqual(player.reserved_cards, cards[:2])
        self.assertIn(cards[-1], player.cards[cards[-1].token])
        self.assertEqual(app.state.market, market)
        self.assertEqual(app.state.decks, decks)
        app.strategy = GreedyAI()
        app.refresh()
        stack = app.computer.reserved.stack
        stack.event_generate('<Motion>', x=75, y=100)
        stack.event_generate('<Button-1>', x=75, y=100)
        self.assertIsNone(app.state.selection.card)

    def test_reserved_cards_are_last_disabled_block_and_refresh_in_place(self):
        app = self.app
        cards = app.state.market[1][:3]
        for player, panel in zip(app.state.players, (app.player, app.computer)):
            reserved = panel.reserved
            self.assertFalse(reserved.winfo_ismapped())
            player.add_card(cards[0])
            player.reserved_cards.extend(cards)
            app.refresh()
            self.root.update()
            self.assertTrue(reserved.winfo_ismapped())
            owned = panel.columns[cards[0].token]
            self.assertLess(owned.winfo_rootx() + owned.winfo_width(), reserved.winfo_rootx())
            items = list(reserved.stack.find_all())
            for card, item, overlay in zip(cards, reserved.card_items, reserved.overlay_items):
                self.assertEqual(reserved.stack.itemcget(item, 'image'), str(load_image(reserved, card.id)))
                self.assertEqual(reserved.stack.itemcget(overlay, 'image'),
                                 str(load_image(reserved, 'disabled')))
                self.assertEqual(reserved.stack.coords(item), reserved.stack.coords(overlay))
                self.assertEqual(items.index(overlay), items.index(item) + 1)
                self.assertEqual(reserved.stack.itemcget(overlay, 'state'), 'normal')
            reserved.stack.event_generate('<Button-1>', x=75, y=100)
            if player is app.state.current_player:
                self.assertIn(app.state.selection.card, player.reserved_cards)
                app.select_card(app.state.selection.card)
            else:
                self.assertIsNone(app.state.selection.card)
            player.reserved_cards.pop(0)
            app.refresh()
            self.assertEqual(reserved.stack.itemcget(reserved.card_items[0], 'image'),
                             str(load_image(reserved, cards[1].id)))
            self.assertEqual(reserved.stack.itemcget(reserved.card_items[-1], 'state'), 'hidden')
            self.assertEqual(reserved.stack.itemcget(reserved.overlay_items[-1], 'state'), 'hidden')
            player.reserved_cards.clear()
            app.refresh()
            self.root.update()
            self.assertFalse(reserved.winfo_ismapped())
            player.reserved_cards.extend(cards)
            app.refresh()
            self.root.update()
            self.assertTrue(reserved.winfo_ismapped())
            self.assertEqual(set(reserved.stack.find_all()), set(items))
        app.new_game()
        self.root.update()
        self.assertFalse(app.player.reserved.winfo_ismapped())
        self.assertFalse(app.computer.reserved.winfo_ismapped())
