"""Array-based search positions, legal moves, and reversible execution.

Convert the desktop position once with State.from_game(source), then search
using only simulation objects. Player data lives in state.players[player_index].
Token vectors follow game.constants.TOKENS;
card.token is an integer token index; card.tier and all tier arrays use 0–2.
All cards, including owned cards, live
in one stable cards array. market_indices holds three rows of card indices;
deck_starts/deck_ends delimit each tier's unread range in that array. Cards
track owner and purchased status (owned, unpurchased means reserved).
Market slot order is irrelevant. Every market draw advances deck_starts, even
past deck_ends for empty draws; undo uses that cursor to reverse replacements.
Moves reference only card_index and noble_index. Nobles stay in a stable list;
their owner is None while available, then the owning player's index.
Both players take three distinct gems, or one of every available gem color
when fewer than three remain; matching pairs require four gems in supply.
Required returns are combined into the same move.
Reservations are allowed without gold in supply; they grant gold only if available.
Moves store only the awarded noble's index. Buy moves use the purchased bonus;
other moves include any noble already qualified for at the start of the turn.
The buy action takes a market card; buy_reserved purchases an owned reservation
without changing the market or drawing a replacement.
The caller owns turn order and supplies the player index (0 or 1). Use
finished(player_index) and winner(player_index) with the player who would move next;
final-round status is derived from scores.

    position = State.from_game(source)
    player_index = source.turn.active_player
    for move in generate_moves(position, player_index):
        move.make(position, player_index)
        try:
            # Evaluate or recurse using this same position and 1 - player_index.
            ...
        finally:
            move.unmake(position, player_index)

Take and Reserve include required returns and finish the turn in one move.
Token vectors are signed net transfers: positive takes, negative returns.
Buy vectors contain the actual payment as negative counts, including gold.
Deck cursors avoid shifting cards during search. Execution uses the supplied deck order;
an AI must sample unknown order rather than exploit the real hidden order.
"""

from .state import Card, Noble, Player, State
from .generate import generate_moves
from .move import Move

__all__ = ["Card", "Noble", "Player", "State", "Move", "generate_moves"]
