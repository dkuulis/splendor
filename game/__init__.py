"""Plain Python objects, independent of the UI and game rules.

Gem dictionaries map colors to counts; missing colors mean zero.
Player card dictionaries map card IDs to Card objects; {} means no cards.
Decks are ordered lists of cards. Market rows contain cards or None for empty
slots. The preview factory supplies sample data, not a new-game deal.
"""

from .card import Card
from .player import Player
from .state import State
from .turn import Turn
