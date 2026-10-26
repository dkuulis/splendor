import unittest
from unittest.mock import Mock

from app.app import App
from game.constants import RUBY, GOLD
from game import Card, State


class SelectionRefreshTests(unittest.TestCase):
    def test_selections_leave_board_and_ai_lifecycle_alone(self):
        app = App.__new__(App)
        app.state = State()
        app.strategy = None
        app.supply = Mock()
        app.market = Mock()
        app.player = Mock()
        app.computer = Mock()
        app.selection = Mock()
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
        self.assertEqual(app.selection.refresh.call_count, 3)
        app.refresh.assert_not_called()
        app.cancel_ai.assert_not_called()
        app.size_window.assert_not_called()
        app.player_divider.refresh.assert_not_called()
        app.computer_divider.refresh.assert_not_called()
        self.assertEqual(app.state.turn.active_player, 0)

    def test_card_clicks_delegate_transitions_to_selection(self):
        app = App.__new__(App)
        app.state = State()
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
        self.assertEqual(app.state.selection.action_kind, 'buy')
        self.assertIs(app.state.selection.card, other)
        self.assertEqual(app.state.selection.tokens, {})
        app.select_token(GOLD)
        app.select_card(reserved)
        self.assertEqual(app.state.selection.action_kind, 'buy')
        self.assertIs(app.state.selection.card, reserved)
        self.assertEqual(app.state.selection.tokens, {})


if __name__ == '__main__':
    unittest.main()
