"""Computer strategies.

Register a display name and strategy class in STRATEGIES to expose it in the
UI. Each strategy implements play_turn(state), clears any pending selection,
selects its action, and calls State.perform_action() exactly once. Strategies
must not depend on Tkinter.
"""

from .pass_only import PassOnlyAI
from .greedy import GreedyAI

STRATEGIES = {"Pass-only AI": PassOnlyAI, "Greedy AI": GreedyAI}
