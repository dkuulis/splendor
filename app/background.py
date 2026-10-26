"""Paint one continuous tabletop through Tk's opaque layout containers."""

import tkinter as tk
from tkinter import ttk

from .assets import load_image
from .styles import BACKGROUND_CORNER_SIZE


def source_coordinates(length, source_length):
    border = BACKGROUND_CORNER_SIZE
    if length <= 2 * border:
        return [position * source_length // length for position in range(length)]
    # Preserve both ends at native size; stretch only the undecorated middle.
    middle = [border + position * (source_length - 2 * border) // (length - 2 * border)
              for position in range(length - 2 * border)]
    return list(range(border)) + middle + list(range(source_length - border, source_length))


class Background:
    def __init__(self, root, excluded):
        self.root = root
        self.excluded = excluded
        self.source = load_image(root, "background")
        self.image = tk.PhotoImage(master=root)
        self.size = None
        self.surfaces = {}
        self.pending = None
        root.bind("<Configure>", self.schedule, add="+")
        root.bind("<Destroy>", self.destroy, add="+")
        self.schedule()

    def schedule(self, event=None):
        if self.pending is None:
            self.pending = self.root.after_idle(self.draw)

    def destroy(self, event):
        if event.widget is self.root and self.pending is not None:
            self.root.after_cancel(self.pending)
            self.pending = None

    def register(self, widget):
        if widget in self.excluded:
            return
        children = widget.winfo_children()
        if widget not in self.surfaces:
            if isinstance(widget, (tk.Frame, ttk.Frame)):
                label = tk.Label(widget, borderwidth=0, highlightthickness=0)
                # ttk's padding counts as an internal border to place(). Paint
                # over it too; classic frames retain their active-player outline.
                label.place(x=0, y=0, relwidth=1, relheight=1,
                            bordermode="ignore" if isinstance(widget, ttk.Frame) else "inside")
                label.lower()
                self.surfaces[widget] = (label, None, tk.PhotoImage(master=self.root))
            elif isinstance(widget, tk.Canvas):
                item = widget.create_image(0, 0, anchor="nw", tags=("background",))
                widget.tag_lower(item)
                self.surfaces[widget] = (widget, item, tk.PhotoImage(master=self.root))
        for child in children:
            self.register(child)

    def resize(self, width, height):
        self.image.configure(width=width, height=height)
        # Tk only offers integer zoom factors. Resample in two passes of
        # one-pixel strips for arbitrary window sizes without a runtime dependency.
        # Fixed ends on both axes preserve all four corners. Edge strips stretch
        # along one axis and the center along both, without repeating artwork.
        source_width, source_height = self.source.width(), self.source.height()
        horizontal = tk.PhotoImage(master=self.root, width=width, height=source_height)
        for x, source_x in enumerate(source_coordinates(width, source_width)):
            horizontal.tk.call(str(horizontal), "copy", str(self.source),
                               "-from", source_x, 0, source_x + 1, source_height,
                               "-to", x, 0)
        for y, source_y in enumerate(source_coordinates(height, source_height)):
            self.image.tk.call(str(self.image), "copy", str(horizontal),
                               "-from", 0, source_y, width, source_y + 1,
                               "-to", 0, y)
        self.size = (width, height)

    def draw(self):
        self.pending = None
        width, height = self.root.winfo_width(), self.root.winfo_height()
        if self.size != (width, height):
            self.resize(width, height)
        self.register(self.root)
        for widget, (surface, item, image) in self.surfaces.items():
            if not surface.winfo_ismapped():
                continue
            x = surface.winfo_rootx() - self.root.winfo_rootx()
            y = surface.winfo_rooty() - self.root.winfo_rooty()
            w = min(surface.winfo_width(), width - x)
            h = min(surface.winfo_height(), height - y)
            if w <= 0 or h <= 0:
                continue
            image.configure(width=w, height=h)
            image.tk.call(str(image), "copy", str(self.image),
                          "-from", x, y, x + w, y + h, "-to", 0, 0)
            if item is None:
                surface.configure(image=image)
            else:
                surface.itemconfigure(item, image=image)
