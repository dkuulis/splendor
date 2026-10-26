"""Computer strategies.

Register a command-line name and strategy class in STRATEGIES to expose it via
--ai. Each strategy implements make_selection(state, selection), clears pending
choices, and prepares one legal selection without changing State. App dispatches
the action after the strategy returns. Strategies must not depend on Tkinter.
"""

from .pass_only import PassOnlyAI
from .greedy import GreedyAI
from .greedy2 import Greedy2AI
from .greedy_sim import GreedySimAI
from .minimax import MinimaxAI

STRATEGIES = {"pass-only": PassOnlyAI, "greedy": GreedyAI, "greedy2": Greedy2AI,
              "greedy_sim": GreedySimAI, "minimax": MinimaxAI}
