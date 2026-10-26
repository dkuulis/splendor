import contextlib
import io
import unittest
from unittest.mock import patch

import main
from ai import GreedyAI, PassOnlyAI


class CommandLineTests(unittest.TestCase):
    def test_selected_strategy_is_passed_to_app(self):
        for arguments, expected in (([], GreedyAI), (['--ai', 'greedy'], GreedyAI),
                                    (['--ai', 'pass-only'], PassOnlyAI),
                                    (['--ai', 'manual'], type(None))):
            with self.subTest(arguments=arguments), patch('sys.argv', ['main.py', *arguments]), \
                    patch('main.tk.Tk') as root, patch('main.App') as app, \
                    patch('main.create_initial_state') as state:
                main.main()
                self.assertEqual(app.call_args.args[:2], (root.return_value, state.return_value))
                self.assertIsInstance(app.call_args.args[2], expected)
                root.return_value.mainloop.assert_called_once_with()

    def test_help_and_invalid_choice_exit_before_creating_window(self):
        for arguments, code in ((['--help'], 0), (['--ai', 'unknown'], 2)):
            with self.subTest(arguments=arguments), patch('sys.argv', ['main.py', *arguments]), \
                    patch('main.tk.Tk') as root, contextlib.redirect_stdout(io.StringIO()), \
                    contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    main.main()
                self.assertEqual(raised.exception.code, code)
                root.assert_not_called()
