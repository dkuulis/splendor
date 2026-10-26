import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from app.app import App
from app.log import Log
from game.constants import RUBY
from game import Card, State


class SelectionRefreshTests(unittest.TestCase):
    def test_selections_leave_board_log_and_ai_lifecycle_alone(self):
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
        app.log = Mock()
        app.scores = Mock()
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
        app.log.refresh.assert_not_called()
        app.scores.refresh.assert_not_called()
        self.assertEqual(app.state.turn.active_player, 0)


class LogRefreshTests(unittest.TestCase):
    def make_log(self, at_bottom):
        log = SimpleNamespace(
            items=[1], messages=['Old entry'], displayed_messages=['Old entry'], canvas=Mock(),
            update_scroll_region=Mock(),
        )
        log.canvas.yview.return_value = (0.8, 1.0) if at_bottom else (0.2, 0.4)
        log.canvas.canvasy.return_value = 200
        log.canvas.winfo_height.return_value = 200
        log.canvas.cget.return_value = '0 0 250 1200'
        log.canvas.create_text.return_value = 2
        return log

    def test_unchanged_log_does_not_touch_widgets_or_scroll(self):
        log = self.make_log(False)
        Log.refresh(log, log.messages)
        log.canvas.yview.assert_not_called()
        log.canvas.create_text.assert_not_called()
        log.update_scroll_region.assert_not_called()

    def test_append_preserves_existing_text_and_reading_position(self):
        log = self.make_log(False)
        item = log.items[0]
        log.messages.append('New entry')
        Log.refresh(log, log.messages)
        log.canvas.create_text.assert_called_once()
        self.assertEqual(log.canvas.create_text.call_args.kwargs['text'], 'New entry')
        self.assertEqual(log.items[0], item)
        log.canvas.itemconfigure.assert_not_called()
        log.canvas.delete.assert_not_called()
        log.canvas.yview_moveto.assert_called_once_with(200 / 1200)

    def test_append_follows_latest_when_already_at_bottom(self):
        log = self.make_log(True)
        log.messages.append('New entry')
        Log.refresh(log, log.messages)
        log.canvas.yview_moveto.assert_called_once_with(1)


if __name__ == '__main__':
    unittest.main()
