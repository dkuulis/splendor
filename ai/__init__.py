"""Computer strategies.

Register a display name and strategy class in STRATEGIES to expose it in the
UI. Each strategy implements play_turn(state), performing exactly one legal
action through State's action methods. Strategies must not depend on Tkinter.
"""

from .pass_only import PassOnlyAI

STRATEGIES = {"Pass-only AI": PassOnlyAI}
