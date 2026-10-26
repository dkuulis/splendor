"""Separate each player's holdings from the shared board."""

import tkinter as tk

from .assets import load_image
from .styles import TABLE_BACKGROUND


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
        self.height = self.tiles[False][0].height()
        self.width = None
        self.configure(width=1, height=self.height)
        self.divider = self.create_image(0, 0, anchor="nw", image=self.images[False])
        self.bind("<Configure>", self.resize)

    def resize(self, event):
        if event.width == self.width:
            return
        self.width = event.width
        for active, (left, middle, right) in self.tiles.items():
            image = self.images[active]
            image.configure(width=self.width, height=self.height)
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

    def refresh(self, active):
        self.itemconfigure(self.divider, image=self.images[active])
