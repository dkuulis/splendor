"""Describe the complete game scene without creating or moving Canvas items.

App calls layout after model changes and window resizes, then passes the result
to Renderer. Keys identify display slots rather than the cards occupying them:
a market replacement or Restart can change the image without replacing its
Canvas item. This module only reads State and Selection; their permission
methods determine which descriptions receive click actions.
"""

from game.constants import GOLD, TOKENS
from .styles import (
    WINDOW_MIN_WIDTH, MARKET_CARD_WIDTH, MARKET_CARD_HEIGHT, MARKET_ROW_PADDING,
    NOBLE_SIZE, TOKEN_SIZE, TOKEN_GAP, TOKEN_SPACING, PLAYER_CARD_OFFSET,
    PLAYER_COLUMN_GAP, TOKEN_OVERHANG,
    PLAYER_PANEL_PADDING, ACTION_BUTTON_WIDTH,
    RESTART_BUTTON_HEIGHT, SCORE_CENTER_X,
)


def pile_name(token, count):
    return token.lower() + (str(count) if count > 1 else "")


def layout(state, selection, width, height, image_sizes, manual_turn):
    """Return (keyed image descriptions, minimum size), without touching Tk.

    width and height are the current Canvas dimensions; minimum size is the
    (width, height) needed for native-sized artwork and current player holdings.
    Calculate against at least that minimum while App updates the window bounds.
    image_sizes maps asset names to their native (width, height).

    Each keyed description contains an asset name, top-left x/y position in
    Canvas pixels, visibility, drawing order (higher is in front), and an
    optional action. Panel helpers may use anchors for natural positioning;
    add() converts them to top-left coordinates before emitting the description. A missing element and an
    explicitly invisible element both hide their retained Canvas item.
    Only generated background and divider images request a non-None size.

    Actions are (App method name, arguments) pairs, never captured callbacks.
    manual_turn controls human interaction, including while an AI selection is
    displayed. Decorative overlays share their underlying card's action because
    Tk sends clicks to the topmost image under the pointer.
    """
    elements = {}

    def add(key, image, x, y, anchor="nw", visible=True, action=None, size=None):
        # Keep anchor arithmetic here so every rendered item uses top-left
        # coordinates. Composites use their requested size, artwork its native size.
        if anchor != "nw" and image is not None:
            width, height = size if size is not None else image_sizes[image]
            offset_x, offset_y = {"center": (0.5, 0.5), "se": (1, 1), "w": (0, 0.5)}[anchor]
            x -= width * offset_x
            y -= height * offset_y
        # Emission order defines stacking, including each card's own overlay.
        elements[key] = dict(image=image, x=x, y=y,
                             visible=visible, order=len(elements), action=action, size=size)

    columns = {index: _player_columns(player, image_sizes)
               for index, player in enumerate(state.players)}

    # Establish the shared board's fixed columns and vertical bands first:
    # computer holdings, divider, board, divider, human holdings. Extra window
    # height extends the tabletop; it does not stretch cards or their spacing.
    margin = 20
    row_height = MARKET_CARD_HEIGHT + 2 * MARKET_ROW_PADDING
    noble_width = NOBLE_SIZE + 8
    selection_width = TOKEN_SIZE + 4 * TOKEN_SPACING + ACTION_BUTTON_WIDTH + 24
    market_width = 5 * (MARKET_CARD_WIDTH + 8)
    board_width = noble_width + 12 + selection_width + 12 + market_width
    player_height = MARKET_CARD_HEIGHT + 2 * PLAYER_PANEL_PADDING
    divider_height = max(image_sizes['score_plaque0'][1], image_sizes['divider_inactive_left'][1],
                         image_sizes['victory_laurels'][1])
    holdings_width = max(sum(col[4] for col in cols) + max(0, len(cols) - 1) * PLAYER_COLUMN_GAP
                         + 2 * PLAYER_PANEL_PADDING for cols in columns.values())
    minimum = (max(WINDOW_MIN_WIDTH, board_width + 2 * margin, holdings_width + 2 * margin),
               2 * margin + 2 * player_height + 2 * divider_height + 3 * row_height + 8)
    width, height = max(width, minimum[0]), max(height, minimum[1])
    add(('background',), 'background', 0, 0, size=(width, height))
    board_x = (width - board_width) / 2
    divider_top = margin + player_height
    board_y = divider_top + divider_height + 4
    divider_bottom = board_y + 3 * row_height + 4

    # Panel helpers emit into the same scene in drawing order. They receive
    # explicit bounds; only this entry point arranges the panels themselves.
    for index, y in ((1, margin), (0, divider_bottom + divider_height)):
        _layout_player(add, state, selection, manual_turn, index, columns[index],
                       (margin, y, width - 2 * margin))
    for index, y in ((1, divider_top), (0, divider_bottom)):
        _layout_divider(add, state, image_sizes, index,
                        (margin, y, width - 2 * margin, divider_height))
    _layout_nobles(add, state.nobles, (board_x, board_y, 3 * row_height))
    middle_x = board_x + noble_width + 12
    market_x = middle_x + selection_width + 12
    _layout_market(add, state, selection, manual_turn, (market_x, board_y), row_height)
    _layout_supply(add, state, selection, manual_turn,
                   (middle_x, board_y, selection_width, 2 * row_height))
    selection_y = board_y + 2 * row_height + MARKET_ROW_PADDING
    _layout_selection(add, state, selection, image_sizes, manual_turn,
                      (middle_x, selection_y, selection_width))
    return elements, minimum


def _player_columns(player, image_sizes):
    """Measure occupied columns before pending returns change displayed piles."""
    columns = []
    for token in (*TOKENS, None):
        cards = (player.reserved_cards if token is None else
                 player.nobles if token == GOLD else player.cards[token])
        count = player.tokens.get(token, 0) if token else 0
        if not cards and not count:
            continue
        stack_width = MARKET_CARD_WIDTH + max(0, len(cards) - 1) * PLAYER_CARD_OFFSET
        pile_width = image_sizes[pile_name(token, count)][0] if count else 0
        column_width = max(stack_width + (TOKEN_OVERHANG if count else 0), pile_width)
        columns.append((token, cards, count, stack_width, column_width))
    return columns


def _card_action(card, state, selection, manual_turn):
    """Share a card's permitted action between its artwork and overlay."""
    if manual_turn and selection.can_select_card(card, state):
        return ("select_card", (card,))
    return None


def _layout_player(add, state, selection, manual_turn, index, cols, bounds):
    """Spread occupied columns across (x, y, width), stacking cards and piles.

    None denotes reserved cards; Gold denotes nobles. Measure columns from
    actual holdings so pending returns do not move the surrounding columns.
    """
    x, y, width = bounds
    extra = (width - 2 * PLAYER_PANEL_PADDING
             - sum(col[4] for col in cols) - max(0, len(cols) - 1) * PLAYER_COLUMN_GAP)
    x += PLAYER_PANEL_PADDING
    for token, cards, count, stack_width, column_width in cols:
        allocated = column_width + extra / len(cols)
        left = x + (allocated - column_width) / 2
        start = left + column_width - (TOKEN_OVERHANG if count else 0) - stack_width
        top = y + PLAYER_PANEL_PADDING + (30 if token == GOLD else 0)
        for slot, card in enumerate(cards):
            key = ('player-card', index, token, slot)
            visible = token is not None or card is not selection.card
            action = (_card_action(card, state, selection, manual_turn)
                      if token is None and index == state.turn.active_player else None)
            add(key, card.id, start + slot * PLAYER_CARD_OFFSET, top, visible=visible, action=action)
            if token is None:
                add(('player-overlay', index, slot), 'disabled',
                    start + slot * PLAYER_CARD_OFFSET, top, visible=visible, action=action)
        returned = selection.tokens.get(token, 0) if selection.returning and index == state.turn.active_player else 0
        shown = count - returned
        action = (("select_return_token", (token,)) if manual_turn and index == state.turn.active_player
                  and selection.can_select_return_token(token, state) else None)
        if token is not None and shown:
            add(('player-token', index, token), pile_name(token, shown), left + column_width,
                top + (NOBLE_SIZE if token == GOLD else MARKET_CARD_HEIGHT), anchor='se', action=action)
        x += allocated + PLAYER_COLUMN_GAP


def _layout_divider(add, state, image_sizes, index, bounds):
    """Stretch the divider across its bounds, keeping plaques at native size.

    After completion only a winner is active; a draw highlights neither player.
    """
    x, y, width, divider_height = bounds
    winner = state.turn.finished and state.turn.winner == index
    active = winner if state.turn.finished else state.is_active_player(state.players[index])
    name = 'active' if active else 'inactive'
    add(('divider', index), 'divider_' + name, x, y + divider_height / 2,
        anchor='w', size=(width, image_sizes['divider_' + name + '_left'][1]))
    plaque = 'score_plaque' if active else 'score_plaque_inactive'
    add(('score', index), plaque + str(state.players[index].points),
        x + SCORE_CENTER_X, y + divider_height / 2, anchor='center')
    add(('laurels', index), 'victory_laurels', x + SCORE_CENTER_X,
        y + divider_height / 2, anchor='center', visible=winner)


def _layout_nobles(add, nobles, bounds):
    """Center the noble column vertically within the shared board."""
    x, y, height = bounds
    total = len(nobles) * (NOBLE_SIZE + 2 * MARKET_ROW_PADDING)
    for slot, noble in enumerate(nobles):
        add(('noble', slot), noble.id, x + 4,
            y + (height - total) / 2 + slot * (NOBLE_SIZE + 2 * MARKET_ROW_PADDING) + MARKET_ROW_PADDING)


def _layout_market(add, state, selection, manual_turn, origin, row_height):
    """Keep all deck/card slots allocated, hiding selected or missing artwork."""
    left, top = origin
    for row, tier in enumerate((3, 2, 1)):
        y = top + row * row_height + MARKET_ROW_PADDING
        add(('deck', tier), f'deck_level_{tier}', left + 4, y, visible=bool(state.decks[tier]))
        for slot in range(4):
            card = state.market[tier][slot] if slot < len(state.market[tier]) else None
            visible = card is not None and card is not selection.card
            x = left + (slot + 1) * (MARKET_CARD_WIDTH + 8) + 4
            action = _card_action(card, state, selection, manual_turn)
            add(('market', tier, slot), card.id if card else None, x, y, visible=visible, action=action)
            add(('market-overlay', tier, slot), 'enabled2', x, y,
                visible=visible and manual_turn and not state.return_required and state.can_buy(card), action=action)


def _layout_supply(add, state, selection, manual_turn, bounds):
    """Preview taken tokens in supply; returns only reduce player piles."""
    x, y, width, height = bounds
    for slot, token in enumerate(TOKENS):
        count = state.supply.get(token, 0) - (0 if selection.returning else selection.tokens.get(token, 0))
        action = (('select_token', (token,)) if manual_turn and selection.can_select_token(token, state) else None)
        add(('supply', token), pile_name(token, count) if count > 0 else None,
            x + width * ((slot % 2) + .5) / 2,
            y + height * ((slot // 2) + .5) / 3,
            anchor='center', visible=count > 0, action=action)


def _layout_selection(add, state, selection, image_sizes, manual_turn, bounds):
    """Center selected artwork before the fixed action and Restart controls."""
    origin_x, y, width = bounds
    button_x = origin_x + width - ACTION_BUTTON_WIDTH - 5
    piles = [(token, pile_name(token, selection.tokens[token])) for token in TOKENS if selection.tokens.get(token, 0)]
    pile_width = sum(image_sizes[name][0] for _, name in piles) + max(0, len(piles) - 1) * TOKEN_GAP
    content_width = pile_width + (10 if piles and selection.card else 0) + (MARKET_CARD_WIDTH if selection.card else 0)
    left = origin_x + (button_x - 5 - origin_x - content_width) / 2
    for token, name in piles:
        w = image_sizes[name][0]
        action = (('deselect_token', (token,)) if manual_turn and selection.can_deselect_token(token, state) else None)
        add(('selected-token', token), name, left + w / 2, y + MARKET_CARD_HEIGHT / 2,
            anchor='center', action=action)
        left += w + TOKEN_GAP
    if selection.card:
        x = left + (10 - TOKEN_GAP if piles else 0)
        action = _card_action(selection.card, state, selection, manual_turn)
        add(('selected-card',), selection.card.id, x, y, action=action)
        affordable = manual_turn and state.can_buy(selection.card)
        add(('selected-overlay',), 'enabled2' if affordable else 'disabled', x, y, action=action)
    kind = ({0: 'win', 1: 'loose', None: 'tie'}[state.turn.winner] if state.turn.finished else selection.action_kind)
    enabled = manual_turn and selection.can_perform_action(state)
    add(('action',), f'button_{kind}_{"enabled" if enabled else "disabled"}2', button_x, y,
        action=('perform_action', ()) if enabled else None)
    add(('restart',), 'button_restart_enabled', button_x,
        y + MARKET_CARD_HEIGHT - RESTART_BUTTON_HEIGHT, action=('new_game', ()))
