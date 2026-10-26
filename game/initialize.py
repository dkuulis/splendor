"""Card definitions transcribed from the supplied list, in its original order."""

import random

from .card import Card
from .state import State


def create_initial_state(seed=None):
    """Shuffle and deal a new game; an optional seed makes the deal repeatable."""
    state = State()
    rng = random.Random(seed)
    for tier, deck in enumerate(create_decks(), 1):
        rng.shuffle(deck)
        state.market[tier] = deck[:4]
        state.decks[tier] = deck[4:]
    return state


def create_decks():
    """Return fresh level 1, 2, and 3 decks at indices 0, 1, and 2."""
    return [
        [  # Level 1
            Card("card-001", 1, "Onyx", 0, {"Sapphire": 1, "Emerald": 1, "Ruby": 1, "Diamond": 1}),
            Card("card-002", 1, "Onyx", 0, {"Sapphire": 2, "Emerald": 1, "Ruby": 1, "Diamond": 1}),
            Card("card-003", 1, "Onyx", 0, {"Sapphire": 2, "Ruby": 1, "Diamond": 2}),
            Card("card-004", 1, "Onyx", 0, {"Onyx": 1, "Emerald": 1, "Ruby": 3}),
            Card("card-005", 1, "Onyx", 0, {"Emerald": 2, "Ruby": 1}),
            Card("card-006", 1, "Onyx", 0, {"Emerald": 2, "Diamond": 2}),
            Card("card-007", 1, "Onyx", 0, {"Emerald": 3}),
            Card("card-008", 1, "Onyx", 1, {"Sapphire": 4}),
            Card("card-009", 1, "Sapphire", 0, {"Onyx": 1, "Emerald": 1, "Ruby": 1, "Diamond": 1}),
            Card("card-010", 1, "Sapphire", 0, {"Onyx": 1, "Emerald": 1, "Ruby": 2, "Diamond": 1}),
            Card("card-011", 1, "Sapphire", 0, {"Emerald": 2, "Ruby": 2, "Diamond": 1}),
            Card("card-012", 1, "Sapphire", 0, {"Sapphire": 1, "Emerald": 3, "Ruby": 1}),
            Card("card-013", 1, "Sapphire", 0, {"Onyx": 2, "Diamond": 1}),
            Card("card-014", 1, "Sapphire", 0, {"Onyx": 2, "Emerald": 2}),
            Card("card-015", 1, "Sapphire", 0, {"Onyx": 3}),
            Card("card-016", 1, "Sapphire", 1, {"Ruby": 4}),
            Card("card-017", 1, "Diamond", 0, {"Onyx": 1, "Sapphire": 1, "Emerald": 1, "Ruby": 1}),
            Card("card-018", 1, "Diamond", 0, {"Onyx": 1, "Sapphire": 1, "Emerald": 2, "Ruby": 1}),
            Card("card-019", 1, "Diamond", 0, {"Onyx": 1, "Sapphire": 2, "Emerald": 2}),
            Card("card-020", 1, "Diamond", 0, {"Onyx": 1, "Sapphire": 1, "Diamond": 3}),
            Card("card-021", 1, "Diamond", 0, {"Onyx": 1, "Ruby": 2}),
            Card("card-022", 1, "Diamond", 0, {"Onyx": 2, "Sapphire": 2}),
            Card("card-023", 1, "Diamond", 0, {"Sapphire": 3}),
            Card("card-024", 1, "Diamond", 1, {"Emerald": 4}),
            Card("card-025", 1, "Emerald", 0, {"Onyx": 1, "Sapphire": 1, "Ruby": 1, "Diamond": 1}),
            Card("card-026", 1, "Emerald", 0, {"Onyx": 2, "Sapphire": 1, "Ruby": 1, "Diamond": 1}),
            Card("card-027", 1, "Emerald", 0, {"Onyx": 2, "Sapphire": 1, "Ruby": 2}),
            Card("card-028", 1, "Emerald", 0, {"Sapphire": 3, "Emerald": 1, "Diamond": 1}),
            Card("card-029", 1, "Emerald", 0, {"Sapphire": 1, "Diamond": 2}),
            Card("card-030", 1, "Emerald", 0, {"Sapphire": 2, "Ruby": 2}),
            Card("card-031", 1, "Emerald", 0, {"Ruby": 3}),
            Card("card-032", 1, "Emerald", 1, {"Onyx": 4}),
            Card("card-033", 1, "Ruby", 0, {"Onyx": 1, "Sapphire": 1, "Emerald": 1, "Diamond": 1}),
            Card("card-034", 1, "Ruby", 0, {"Onyx": 1, "Sapphire": 1, "Emerald": 1, "Diamond": 2}),
            Card("card-035", 1, "Ruby", 0, {"Onyx": 2, "Emerald": 1, "Diamond": 2}),
            Card("card-036", 1, "Ruby", 0, {"Onyx": 3, "Ruby": 1, "Diamond": 1}),
            Card("card-037", 1, "Ruby", 0, {"Sapphire": 2, "Emerald": 1}),
            Card("card-038", 1, "Ruby", 0, {"Ruby": 2, "Diamond": 2}),
            Card("card-039", 1, "Ruby", 0, {"Diamond": 3}),
            Card("card-040", 1, "Ruby", 1, {"Diamond": 4}),
        ],
        [  # Level 2
            Card("card-041", 2, "Onyx", 1, {"Sapphire": 2, "Emerald": 2, "Diamond": 3}),
            Card("card-042", 2, "Onyx", 1, {"Onyx": 2, "Emerald": 3, "Diamond": 3}),
            Card("card-043", 2, "Onyx", 2, {"Sapphire": 1, "Emerald": 4, "Ruby": 2}),
            Card("card-044", 2, "Onyx", 2, {"Emerald": 5, "Ruby": 3}),
            Card("card-045", 2, "Onyx", 2, {"Diamond": 5}),
            Card("card-046", 2, "Onyx", 3, {"Onyx": 6}),
            Card("card-047", 2, "Sapphire", 1, {"Sapphire": 2, "Emerald": 2, "Ruby": 3}),
            Card("card-048", 2, "Sapphire", 1, {"Onyx": 3, "Sapphire": 2, "Emerald": 3}),
            Card("card-049", 2, "Sapphire", 2, {"Sapphire": 3, "Diamond": 5}),
            Card("card-050", 2, "Sapphire", 2, {"Onyx": 4, "Ruby": 1, "Diamond": 2}),
            Card("card-051", 2, "Sapphire", 2, {"Sapphire": 5}),
            Card("card-052", 2, "Sapphire", 3, {"Sapphire": 6}),
            Card("card-053", 2, "Diamond", 1, {"Onyx": 2, "Emerald": 3, "Ruby": 2}),
            Card("card-054", 2, "Diamond", 1, {"Sapphire": 3, "Ruby": 3, "Diamond": 2}),
            Card("card-055", 2, "Diamond", 2, {"Onyx": 2, "Emerald": 1, "Ruby": 4}),
            Card("card-056", 2, "Diamond", 2, {"Onyx": 3, "Ruby": 5}),
            Card("card-057", 2, "Diamond", 2, {"Ruby": 5}),
            Card("card-058", 2, "Diamond", 3, {"Diamond": 6}),
            Card("card-059", 2, "Emerald", 1, {"Emerald": 2, "Ruby": 3, "Diamond": 3}),
            Card("card-060", 2, "Emerald", 1, {"Onyx": 2, "Sapphire": 3, "Diamond": 2}),
            Card("card-061", 2, "Emerald", 2, {"Onyx": 1, "Sapphire": 2, "Diamond": 4}),
            Card("card-062", 2, "Emerald", 2, {"Sapphire": 5, "Emerald": 3}),
            Card("card-063", 2, "Emerald", 2, {"Emerald": 5}),
            Card("card-064", 2, "Emerald", 3, {"Emerald": 6}),
            Card("card-065", 2, "Ruby", 1, {"Onyx": 3, "Ruby": 2, "Diamond": 2}),
            Card("card-066", 2, "Ruby", 1, {"Onyx": 3, "Sapphire": 3, "Ruby": 2}),
            Card("card-067", 2, "Ruby", 2, {"Sapphire": 4, "Emerald": 2, "Diamond": 1}),
            Card("card-068", 2, "Ruby", 2, {"Onyx": 5, "Diamond": 3}),
            Card("card-069", 2, "Ruby", 2, {"Onyx": 5}),
            Card("card-070", 2, "Ruby", 3, {"Ruby": 6}),
        ],
        [  # Level 3
            Card("card-071", 3, "Onyx", 3, {"Sapphire": 3, "Emerald": 5, "Ruby": 3, "Diamond": 3}),
            Card("card-072", 3, "Onyx", 4, {"Ruby": 7}),
            Card("card-073", 3, "Onyx", 4, {"Onyx": 3, "Emerald": 3, "Ruby": 6}),
            Card("card-074", 3, "Onyx", 5, {"Onyx": 3, "Ruby": 7}),
            Card("card-075", 3, "Sapphire", 3, {"Onyx": 5, "Emerald": 3, "Ruby": 3, "Diamond": 3}),
            Card("card-076", 3, "Sapphire", 4, {"Diamond": 7}),
            Card("card-077", 3, "Sapphire", 4, {"Onyx": 3, "Sapphire": 3, "Diamond": 6}),
            Card("card-078", 3, "Sapphire", 5, {"Sapphire": 3, "Diamond": 7}),
            Card("card-079", 3, "Diamond", 3, {"Onyx": 3, "Sapphire": 3, "Emerald": 3, "Ruby": 5}),
            Card("card-080", 3, "Diamond", 4, {"Onyx": 7}),
            Card("card-081", 3, "Diamond", 4, {"Onyx": 6, "Ruby": 3, "Diamond": 3}),
            Card("card-082", 3, "Diamond", 5, {"Onyx": 7, "Diamond": 3}),
            Card("card-083", 3, "Emerald", 3, {"Onyx": 3, "Sapphire": 3, "Ruby": 3, "Diamond": 5}),
            Card("card-084", 3, "Emerald", 4, {"Sapphire": 7}),
            Card("card-085", 3, "Emerald", 4, {"Sapphire": 6, "Emerald": 3, "Diamond": 3}),
            Card("card-086", 3, "Emerald", 5, {"Sapphire": 7, "Emerald": 3}),
            Card("card-087", 3, "Ruby", 3, {"Onyx": 3, "Sapphire": 5, "Emerald": 3, "Diamond": 3}),
            Card("card-088", 3, "Ruby", 4, {"Emerald": 7}),
            Card("card-089", 3, "Ruby", 4, {"Sapphire": 3, "Emerald": 6, "Ruby": 3}),
            Card("card-090", 3, "Ruby", 5, {"Emerald": 7, "Ruby": 3}),
        ],
    ]
