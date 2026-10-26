import tkinter as tk
from .assets import load_image

from .styles import CARD_BACKGROUND, MARKET_CARD_WIDTH, MARKET_CARD_HEIGHT


class CardPanel(tk.Canvas):
    def __init__(self, parent, card, on_buy=None, affordable=False, owned=False):
        enabled = bool(on_buy and affordable and not owned)
        super().__init__(parent, width=MARKET_CARD_WIDTH, height=MARKET_CARD_HEIGHT,
                         highlightthickness=0, borderwidth=0, background=CARD_BACKGROUND)
        self.images = self.draw(self, card, active=enabled, owned=owned)
        if enabled:
            self.configure(cursor="hand2")
            self.bind("<Button-1>", lambda event: on_buy(card))

    @staticmethod
    def draw(canvas, card, x=0, y=0, active=True, owned=False):
        """Draw card assets and return image references for the caller to retain."""
        names = [card.id]
        if not active and not owned:
            names.append("disabled")
        images = []
        for name in names:
            image = load_image(canvas, name)
            canvas.create_image(x, y, image=image, anchor="nw")
            images.append(image)
        return images
