"""Separate each player's holdings from the shared board."""

import tkinter as tk
from tkinter import font

from .assets import load_image
from .styles import POINTS_FONT, TABLE_BACKGROUND, SCORE_CENTER_X, TEXT_COLOR


class DividerPanel(tk.Canvas):
    def __init__(self, parent):
        super().__init__(parent, background=TABLE_BACKGROUND,
                         highlightthickness=0, borderwidth=0)
        self.tiles = {
            active: [load_image(self, f"divider_{name}_{section}")
                     for section in ("left", "middle", "right")]
            for active, name in ((True, "active"), (False, "inactive"))
        }
        self.images = {active: tk.PhotoImage(master=self) for active in self.tiles}
        self.points_font = font.Font(root=self, font=POINTS_FONT)
        self.plaque_images = {True: load_image(self, "score_plaque"),
                              False: load_image(self, "score_plaque_inactive")}
        self.height = max(self.tiles[False][0].height(), self.plaque_images[False].height(),
                          self.points_font.metrics("linespace") + 12)
        self.width = None
        self.configure(width=1, height=self.height)
        self.divider = self.create_image(0, self.height / 2, anchor="w", image=self.images[False])
        self.plaque = self.create_image(SCORE_CENTER_X, self.height / 2, image=self.plaque_images[False])
        self.points = self.create_text(SCORE_CENTER_X, self.height / 2, text="0",
                                       font=self.points_font, fill=TEXT_COLOR)
        self.bind("<Configure>", lambda event: self.resize())

    def resize(self):
        width = self.winfo_width()
        if width == self.width:
            return
        self.width = width
        for active, (left, middle, right) in self.tiles.items():
            image = self.images[active]
            image.configure(width=self.width, height=left.height())
            image.blank()
            right_x = max(left.width(), self.width - right.width())
            sections = [(left, 0, min(left.width(), self.width))]
            sections.extend((middle, x, min(middle.width(), right_x - x))
                            for x in range(left.width(), right_x, middle.width()))
            sections.append((right, right_x, self.width - right_x))
            for tile, x, width in sections:
                if width > 0:
                    # Tcl's exclusive crop bounds clip the last repeat while
                    # preserving alpha and the native size of the end caps.
                    image.tk.call(str(image), "copy", str(tile),
                                  "-from", 0, 0, width, tile.height(), "-to", x, 0)

    def refresh(self, active, points):
        self.itemconfigure(self.divider, image=self.images[active])
        self.itemconfigure(self.plaque, image=self.plaque_images[active])
        self.itemconfigure(self.points, text=str(points))
        self.resize()
