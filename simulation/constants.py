"""Game constants gateway and shared indices for simulation token vectors."""

from game.constants import GEMS, GOLD, TOKENS, MAX_RESERVATIONS, MAX_TAKE, TARGET_POINTS, TOKEN_LIMIT

GOLD_INDEX = TOKENS.index(GOLD)
GEM_INDICES = tuple(TOKENS.index(token) for token in GEMS)
TOKEN_COUNT = len(TOKENS)
EMPTY_TOKENS = (0,) * TOKEN_COUNT
SINGLE_GOLD = tuple(int(token_index == GOLD_INDEX) for token_index in range(TOKEN_COUNT))
