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

    def test_background_stays_aligned_after_resize_and_new_game(self):
        background = self.app.background
        for width, height in ((1900, 1300), (2560, 1600), (2100, 1450)):
            self.root.geometry(f"{width}x{height}")
            self.root.update()
            self.assertEqual(background.size,
                             (self.root.winfo_width(), self.root.winfo_height()))
            for frame in (self.app.shell, self.app.player.panel, self.app.supply):
                surface, _, _ = background.surfaces[frame]
                self.assertEqual((surface.winfo_x(), surface.winfo_y()), (0, 0))
                self.assertEqual((surface.winfo_width(), surface.winfo_height()),
                                 (frame.winfo_width(), frame.winfo_height()))
            for widget in (self.app.shell, self.app.player.panel,
                           self.app.supply.cells[RUBY], self.app.selection.tokens,
                           self.app.scores):
                surface, item, image = background.surfaces[widget]
                x = surface.winfo_rootx() - self.root.winfo_rootx()
                y = surface.winfo_rooty() - self.root.winfo_rooty()
                self.assertEqual(image.get(10, 10), background.image.get(x + 10, y + 10))
                if item is not None:
                    self.assertEqual(surface.find_all()[0], item)
            # Every corner retains its original pixels and proportions even
            # when the middle of the window is stretched in either direction.
            w, h = background.size
            sw, sh = background.source.width(), background.source.height()
            for dx, dy in ((10, 10), (80, 150), (230, 30), (30, 230), (259, 259)):
                for x, sx in ((dx, dx), (w - 1 - dx, sw - 1 - dx)):
                    for y, sy in ((dy, dy), (h - 1 - dy, sh - 1 - dy)):
                        self.assertEqual(background.image.get(x, y), background.source.get(sx, sy))
            self.assertEqual(background.image.get(w // 2, h // 2),
                             background.source.get(sw // 2, sh // 2))
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
        self.assertEqual(market_items, [panel.find_all() for panels in app.market.slots.values() for panel in panels])
        self.assertIs(app.selection.state, app.state)
        self.assertEqual(app.supply.counts, app.state.supply)
        self.assertEqual([app.scores.itemcget(score, 'text') for score in app.scores.scores],
                         ['0', '0'])
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
        app.market.slots[1][0].select(None)
        self.assertIsNone(app.state.selected_card)
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

    def test_unaffordable_card_selection_blocks_buy_until_affordable(self):
        app = self.app
        panel = app.market.slots[1][0]
        card = panel.card
        card.cost = {RUBY: 2}
        app.refresh()
        panel.event_generate('<Button-1>')
        self.root.update()
        self.assertIs(app.state.selected_card, card)
        self.assertFalse(panel.winfo_ismapped())
        self.assertTrue(app.selection.card.winfo_ismapped())
        self.assertTrue(app.selection.go_button.instate(['disabled']))
        overlay = app.selection.disabled_overlay
        self.assertEqual(app.selection.card.itemcget(overlay, 'image'),
                         str(load_image(app.selection, 'disabled')))
        self.assertEqual(app.selection.card.itemcget(overlay, 'state'), 'normal')
        app.selection.go_button.invoke()
        self.assertEqual(app.state.turn.active_player, 0)
        self.assertIn(card, app.state.market[1])
        app.selection.card.event_generate('<Button-1>')
        self.root.update()
        self.assertIsNone(app.state.selected_card)
        self.assertTrue(panel.winfo_ismapped())
        panel.event_generate('<Button-1>')
        app.state.current_player.tokens[RUBY] = 2
        app.state.supply[RUBY] -= 2
        app.refresh()
        self.assertFalse(app.selection.go_button.instate(['disabled']))
        self.assertEqual(app.selection.card.itemcget(overlay, 'state'), 'hidden')
        app.selection.go_button.invoke()
        self.assertIn(card, app.state.players[0].cards[card.token])
        self.assertEqual(app.state.players[0].tokens, {})
        self.assertEqual(app.state.turn.active_player, 1)

    def test_owned_gold_enables_buy_and_clears_disabled_overlay(self):
        app = self.app
        card = app.state.market[1][0]
        card.cost = {RUBY: 2}
        app.select_card(card)
        self.assertTrue(app.selection.go_button.instate(['disabled']))
        app.state.current_player.tokens[GOLD] = 2
        app.state.supply[GOLD] -= 2
        app.refresh()
        self.assertEqual(app.selection.go_button.cget('text'), 'Buy')
        self.assertFalse(app.selection.go_button.instate(['disabled']))
        self.assertEqual(app.selection.card.itemcget(app.selection.disabled_overlay, 'state'), 'hidden')
        app.selection.go_button.invoke()
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
        self.assertEqual(app.state.selected_tokens, {GOLD: 1})
        self.assertEqual(app.selection.tokens.itemcget(app.selection.items[GOLD], 'state'), 'normal')
        self.assertTrue(app.selection.go_button.instate(['disabled']))
        app.select_token(RUBY)
        self.assertEqual(app.state.selected_tokens, {RUBY: 1})
        self.assertEqual(app.selection.tokens.itemcget(app.selection.items[GOLD], 'state'), 'hidden')
        self.assertFalse(app.selection.go_button.instate(['disabled']))
        app.select_token(GOLD)
        self.assertEqual(app.state.selected_tokens, {GOLD: 1})
        self.assertEqual(app.selection.tokens.itemcget(app.selection.items[RUBY], 'state'), 'hidden')
        self.assertTrue(app.selection.go_button.instate(['disabled']))
        app.selection.go_button.invoke()
        self.assertEqual(app.state.players[0].tokens, {})
        self.assertEqual(app.state.turn.active_player, 0)
        x, y = app.selection.tokens.coords(app.selection.items[GOLD])
        app.selection.tokens.event_generate('<Motion>', x=int(x), y=int(y))
        app.selection.tokens.event_generate('<Button-1>', x=int(x), y=int(y))
        self.root.update()
        self.assertEqual(app.state.selected_tokens, {})
        self.assertFalse(app.selection.go_button.instate(['disabled']))
        app.select_token(RUBY)
        app.selection.go_button.invoke()
        self.assertEqual(app.state.players[0].tokens, {RUBY: 1})

    def test_gold_and_selected_card_are_visible_together(self):
        app = self.app
        card = app.state.market[1][0]
        card.cost = {}
        app.select_card(card)
        app.supply.pick(GOLD)
        self.root.update()
        self.assertIs(app.state.selected_card, card)
        self.assertFalse(app.market.slots[1][0].winfo_ismapped())
        self.assertTrue(app.selection.card.winfo_ismapped())
        self.assertTrue(app.selection.tokens.winfo_ismapped())
        self.assertLess(app.selection.card.winfo_rootx() + app.selection.card.winfo_width(),
                        app.selection.tokens.winfo_rootx())
        self.assertEqual(app.selection.go_button.cget('text'), 'Reserve')
        self.assertFalse(app.selection.go_button.instate(['disabled']))
        app.selection.deselect(GOLD)
        self.root.update()
        self.assertIs(app.state.selected_card, card)
        self.assertFalse(app.selection.tokens.winfo_ismapped())
        self.assertFalse(app.selection.go_button.instate(['disabled']))
        app.select_token(GOLD)
        app.selection.go_button.invoke()
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
                self.assertEqual(app.selection.go_button.cget('text'), 'Reserve')
                self.assertTrue(app.selection.go_button.instate(['disabled']))
                app.selection.go_button.invoke()
                self.assertIs(app.state.selected_card, card)
                self.assertEqual(app.state.turn.active_player, 0)
                player.tokens.clear()
                player.reserved_cards.clear()
        app.refresh()
        self.assertFalse(app.selection.go_button.instate(['disabled']))

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
        self.assertIsNone(app.state.selected_card)
        stack = app.player.reserved.stack
        for index, card in enumerate(cards):
            x, y = stack.coords(app.player.reserved.card_items[index])
            stack.event_generate('<Motion>', x=int(x) + 10, y=int(y) + 100)
            stack.event_generate('<Button-1>', x=int(x) + 10, y=int(y) + 100)
            self.assertIs(app.state.selected_card, card)
            self.assertEqual(app.selection.go_button.cget('text'), 'Buy')
            self.assertFalse(app.selection.go_button.instate(['disabled']))
            for slot, item in enumerate(app.player.reserved.card_items):
                expected = 'hidden' if slot == index else 'normal'
                self.assertEqual(stack.itemcget(item, 'state'), expected)
                self.assertEqual(stack.itemcget(app.player.reserved.overlay_items[slot], 'state'), expected)
            app.refresh()
            self.assertEqual(stack.itemcget(app.player.reserved.card_items[index], 'state'), 'hidden')
            app.selection.card.select(None)
            self.assertIsNone(app.state.selected_card)
            self.assertEqual(stack.itemcget(app.player.reserved.card_items[index], 'state'), 'normal')
            app.select_card(card)
            app.select_token(GOLD)
            self.assertEqual(app.state.selected_tokens, {})
        market = {tier: list(row) for tier, row in app.state.market.items()}
        decks = {tier: list(row) for tier, row in app.state.decks.items()}
        app.selection.go_button.invoke()
        self.assertEqual(player.reserved_cards, cards[:2])
        self.assertIn(cards[-1], player.cards[cards[-1].token])
        self.assertEqual(app.state.market, market)
        self.assertEqual(app.state.decks, decks)
        app.control.set('Greedy AI')
        app.change_control()
        stack = app.computer.reserved.stack
        stack.event_generate('<Motion>', x=75, y=100)
        stack.event_generate('<Button-1>', x=75, y=100)
        self.assertIsNone(app.state.selected_card)

    def test_log_scroll_and_label_reuse(self):
        app = self.app
        app.state.log.extend(f'Message {index}' for index in range(100))
        app.log.refresh(app.state.log)
        self.root.update()
        self.assertGreaterEqual(app.log.canvas.yview()[1], 0.999)
        labels = list(app.log.labels)
        app.log.canvas.yview_moveto(0.3)
        top = app.log.canvas.canvasy(0)
        app.state.log.append('New entry')
        app.log.refresh(app.state.log)
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
                self.assertIn(app.state.selected_card, player.reserved_cards)
                app.select_card(app.state.selected_card)
            else:
                self.assertIsNone(app.state.selected_card)
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
