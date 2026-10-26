"""Plain Python objects, independent of the UI and game rules.

Token dictionaries map token types to counts; missing types mean zero.
Player card dictionaries map card IDs to Card objects; {} means no cards.
Player nobles are lists of owned Noble objects; [] means no nobles.
State nobles are a list of available nobles.
Decks and market rows are lists of cards with all three tier keys present;
empty tiers use empty lists.
"""

from .card import Card
from .noble import Noble
from .player import Player
from .state import State
from .turn import Turn
