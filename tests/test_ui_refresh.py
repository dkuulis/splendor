import unittest
from unittest.mock import Mock

from ai import GreedyAI, PassOnlyAI
from app.app import App
from game.constants import RUBY, GOLD
from game import Card, State
from game.selection import Selection


class SelectionRefreshTests(unittest.TestCase):
    def test_app_executes_each_ai_selection_once(self):
        for kind in ('pass', 'buy', 'take'):
            with self.subTest(kind=kind):
                app = App.__new__(App)
                app.state = State()
                app.selection = Selection()
                app.state.turn.active_player = 1
                player = app.state.current_player
                card = Card('target', 1, RUBY, 1, {RUBY: 1} if kind == 'take' else {})
                if kind != 'pass':
                    app.state.market[1] = [card]
                app.selection.select_token(RUBY, app.state)
                app.strategy = Mock(wraps=PassOnlyAI() if kind == 'pass' else GreedyAI())
                app.root = Mock()
                app.refresh_selection = Mock()
                app.refresh = Mock()

                app.perform_ai_selection()

                app.strategy.make_selection.assert_called_once_with(app.state, app.selection)
                self.assertEqual(app.state.turn.active_player, 1)
                self.assertEqual(player.tokens, {})
                self.assertEqual(player.cards[RUBY], [])
                self.assertEqual(app.selection.action_kind, kind)
                app.refresh_selection.assert_called_once_with()
                app.refresh.assert_not_called()
                self.assertEqual(app.pending_ai, app.root.after.return_value)

                delay, execute = app.root.after.call_args.args
                self.assertGreater(delay, 0)
                execute()

                self.assertEqual(app.state.turn.consecutive_passes, 1 if kind == 'pass' else 0)
                self.assertEqual(app.state.turn.active_player, 0)
                self.assertEqual(player.tokens, {RUBY: 1} if kind == 'take' else {})
                self.assertEqual(player.cards[RUBY], [card] if kind == 'buy' else [])
                self.assertEqual(app.selection.action_kind, 'pass')
                self.assertIsNone(app.pending_ai)
                app.refresh.assert_called_once_with()

    def test_selections_leave_board_and_ai_lifecycle_alone(self):
        app = App.__new__(App)
        app.state = State()
        app.selection = Selection()
        app.strategy = None
        app.supply = Mock()
        app.market = Mock()
        app.player = Mock()
        app.computer = Mock()
        app.selection_panel = Mock()
        app.refresh = Mock()
        app.cancel_ai = Mock()
        app.size_window = Mock()
        app.player_divider = Mock()
        app.computer_divider = Mock()
        card = Card('selected', 1, RUBY, 0, {})
        app.state.market[1].append(card)

        app.select_card(card)
        app.market.refresh_selection.assert_called_with(card)
        app.select_token(RUBY)
        app.market.refresh_selection.assert_called_with(None)
        app.deselect_token(RUBY)

        self.assertEqual(app.supply.refresh.call_count, 3)
        self.assertEqual(app.selection_panel.refresh.call_count, 3)
        app.selection_panel.refresh.assert_called_with(app.state, app.selection, enabled=True)
        app.refresh.assert_not_called()
        app.cancel_ai.assert_not_called()
        app.size_window.assert_not_called()
        app.player_divider.refresh.assert_not_called()
        app.computer_divider.refresh.assert_not_called()
        self.assertEqual(app.state.turn.active_player, 0)

    def test_card_clicks_delegate_transitions_to_selection(self):
        app = App.__new__(App)
        app.state = State()
        app.selection = Selection()
        app.strategy = None
        app.refresh_selection = Mock()
        first = Card('first', 1, RUBY, 0, {})
        other = Card('other', 1, RUBY, 0, {})
        reserved = Card('reserved', 1, RUBY, 0, {})
        app.state.market[1] = [first, other]
        app.state.current_player.reserved_cards = [reserved]
        app.select_card(first)
        app.select_token(GOLD)
        app.select_card(other)
        self.assertEqual(app.selection.action_kind, 'buy')
        self.assertIs(app.selection.card, other)
        self.assertEqual(app.selection.tokens, {})
        app.select_token(GOLD)
        app.select_card(reserved)
        self.assertEqual(app.selection.action_kind, 'buy')
        self.assertIs(app.selection.card, reserved)
        self.assertEqual(app.selection.tokens, {})


if __name__ == '__main__':
    unittest.main()
