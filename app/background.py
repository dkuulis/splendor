"""Paint one continuous tabletop through Tk's opaque layout containers."""

import tkinter as tk
from tkinter import ttk

from .assets import load_image


def scale_fragment(master, source, width, height):
    if (width, height) == (source.width(), source.height()):
        return source
    # Tk supports only integer zoom factors; copy resampled pixel strips to
    # stretch each fragment without tiling or adding a runtime dependency.
    horizontal = source
    if width != source.width():
        horizontal = tk.PhotoImage(master=master, width=width, height=source.height())
        for x in range(width):
            sx = x * source.width() // width
            horizontal.tk.call(str(horizontal), "copy", str(source),
                               "-from", sx, 0, sx + 1, source.height(), "-to", x, 0)
    if height == source.height():
        return horizontal
    scaled = tk.PhotoImage(master=master, width=width, height=height)
    for y in range(height):
        sy = y * source.height() // height
        scaled.tk.call(str(scaled), "copy", str(horizontal),
                       "-from", 0, sy, width, sy + 1, "-to", 0, y)
    return scaled


class Background:
    def __init__(self, root, excluded):
        self.root = root
        self.excluded = excluded
        self.fragments = {
            (row, column): load_image(root, f"background_{vertical}_{horizontal}")
            for row, vertical in enumerate(("top", "middle", "bottom"))
            for column, horizontal in enumerate(("left", "center", "right"))
        }
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
        corner = self.fragments[0, 0]
        edge_width = min(corner.width(), width // 2)
        edge_height = min(corner.height(), height // 2)
        xs = (0, edge_width, width - edge_width, width)
        ys = (0, edge_height, height - edge_height, height)
        for (row, column), fragment in self.fragments.items():
            w = xs[column + 1] - xs[column]
            h = ys[row + 1] - ys[row]
            if w and h:
                scaled = scale_fragment(self.root, fragment, w, h)
                self.image.tk.call(str(self.image), "copy", str(scaled),
                                   "-to", xs[column], ys[row])
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
