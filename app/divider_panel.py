"""Separate each player's holdings from the shared board."""

import tkinter as tk

from .assets import load_image
from .styles import TABLE_BACKGROUND


class DividerPanel(tk.Canvas):
    def __init__(self, parent):
        super().__init__(parent, background=TABLE_BACKGROUND,
                         highlightthickness=0, borderwidth=0)
        self.images = {active: self.load_rail(name)
                       for active, name in ((True, "active"), (False, "inactive"))}
        image = self.images[False]
        self.configure(width=image.width(), height=image.height())
        self.divider = self.create_image(image.width() / 2, image.height() / 2, image=image)
        self.bind("<Configure>", self.resize)

    def load_rail(self, name):
        source = load_image(self, f"divider_{name}")
        image = tk.PhotoImage(master=self, width=1200, height=52)
        # Copy the end sections and bridge the ornament with an adjacent rail
        # segment. Tcl's exclusive crop bounds preserve the source alpha.
        for left, right, destination in ((0, 560, 0), (480, 560, 560), (640, 1200, 640)):
            image.tk.call(str(image), "copy", str(source),
                          "-from", left, 22, right, 74, "-to", destination, 0)
        return image

    def resize(self, event):
        self.coords(self.divider, event.width / 2, event.height / 2)

    def refresh(self, active):
        self.itemconfigure(self.divider, image=self.images[active])
