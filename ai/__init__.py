"""Computer strategies.

Register a command-line name and strategy class in STRATEGIES to expose it via
--ai. Each strategy implements make_selection(state, selection), clears pending
choices, and prepares one legal selection without changing State. App dispatches
the action after the strategy returns. Strategies must not depend on Tkinter.
"""

from .pass_only import PassOnlyAI
from .greedy import GreedyAI

STRATEGIES = {"pass-only": PassOnlyAI, "greedy": GreedyAI}
