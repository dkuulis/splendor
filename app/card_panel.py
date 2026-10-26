import tkinter as tk

from game.constants import COLORS

from .drawing import draw_cost, draw_gem
from .styles import (
    CARD_BACKGROUND,
    CARD_BORDER_WIDTH,
    CARD_DETAIL_FONT,
    CARD_POINTS_PADDING,
    COST_GEM_RADIUS,
    COST_GEM_SPACING,
    DISABLED_CARD_BORDER,
    DISABLED_PALETTE,
    GEM_RADIUS,
    MARKET_CARD_WIDTH,
    MARKET_CARD_HEIGHT,
    OUTLINE_PALETTE,
    PALETTE,
    POINTS_FONT,
    TEXT_PALETTE,
)


class CardPanel(tk.Canvas):
    def __init__(self, parent, card, on_buy=None, affordable=False, owned=False):
        enabled = bool(on_buy and affordable and not owned)
        super().__init__(parent, width=MARKET_CARD_WIDTH, height=MARKET_CARD_HEIGHT,
                         highlightthickness=0, borderwidth=0, background=CARD_BACKGROUND)
        self.draw(self, card, active=enabled or owned, owned=owned)
        if enabled:
            self.configure(cursor="hand2")
            self.bind("<Button-1>", lambda event: on_buy(card))

    @staticmethod
    def draw(canvas, card, x=0, y=0, active=True, owned=False):
        """Draw a complete card, also reusable beneath gems in player stacks."""
        palette = PALETTE if active else DISABLED_PALETTE
        border = OUTLINE_PALETTE[card.color] if active else DISABLED_CARD_BORDER
        if owned:
            border = DISABLED_PALETTE[card.color]
        right = x + MARKET_CARD_WIDTH
        bottom = y + MARKET_CARD_HEIGHT
        canvas.create_rectangle(x, y, right, bottom,
                                fill=CARD_BACKGROUND, outline="")
        canvas.create_rectangle(x, y, right, y + 62,
                                fill=palette[card.color], outline="")
        if card.points:
            canvas.create_text(x + CARD_POINTS_PADDING, y + 34, text=str(card.points), anchor="w",
                               fill=TEXT_PALETTE[card.color], font=POINTS_FONT)
        draw_gem(canvas, card.color, right - 11 - GEM_RADIUS, y + 31, GEM_RADIUS,
                 outline=TEXT_PALETTE[card.color], width=2)

        costs = [(color, card.cost[color]) for color in COLORS if card.cost.get(color, 0)]
        cost_x = x + 7 + COST_GEM_SPACING / 2
        cost_top = bottom - 7 - len(costs) * COST_GEM_SPACING
        for index, (color, amount) in enumerate(costs):
            cost_y = cost_top + (index + 0.5) * COST_GEM_SPACING
            draw_cost(canvas, color, cost_x, cost_y, COST_GEM_RADIUS)
            canvas.create_text(cost_x, cost_y, text=str(amount),
                               fill=TEXT_PALETTE[color], font=CARD_DETAIL_FONT)

        inset = CARD_BORDER_WIDTH / 2
        canvas.create_rectangle(x + inset, y + inset, right - inset, bottom - inset,
                                outline=border, width=CARD_BORDER_WIDTH)
