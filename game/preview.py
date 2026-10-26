from .card import Card
from .constants import COLORS
from .state import State


def create_preview_state():
    """Build sample objects without connecting them to the UI."""
    state = State()
    state.bank = dict(zip(COLORS, (4, 3, 2, 4, 1)))
    for tier in (1, 2, 3):
        cards = []
        for slot in range(20):
            cost = {
                COLORS[(slot + offset + 1) % 5]: max(1, tier + 1 - offset)
                for offset in range(4 if slot % 4 >= 2 else 2)
            }
            cards.append(Card(
                f"preview-{tier}-{slot}", tier, COLORS[(slot + tier) % 5],
                (0, 2, 4)[tier - 1], cost,
            ))
        state.market[tier] = cards[:4]
        state.decks[tier] = cards[4:]

    human, computer = state.players
    human.gems = {"Sapphire": 1, "Emerald": 2, "Onyx": 1}
    computer.gems = {"Diamond": 1, "Sapphire": 2, "Ruby": 1}
    for player, cards in (
        (human, [Card("preview-owned-0", 1, "Diamond", 0),
                 Card("preview-owned-1", 1, "Ruby", 0)]),
        (computer, [Card("preview-owned-2", 2, "Sapphire", 2),
                    Card("preview-owned-3", 1, "Onyx", 0)]),
    ):
        player.cards = {card.id: card for card in cards}
    return state
