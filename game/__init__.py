"""Plain Python objects, independent of the UI and game rules.

Gem dictionaries map colors to counts; missing colors mean zero.
Player card dictionaries map card IDs to Card objects; {} means no cards.
Decks and market rows are lists of cards with all three tier keys present;
empty tiers use empty lists.
"""

from .card import Card
from .player import Player
from .state import State
from .turn import Turn
