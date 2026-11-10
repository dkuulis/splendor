"""Compose the nine background fragments for one Canvas image."""

import tkinter as tk
from .assets import load_image


def scale_fragment(master, source, width, height):
    """Resize one fragment with nearest-neighbor sampling, reusing it if unchanged."""
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
    def __init__(self, root):
        self.root = root
        self.fragments = {
            (row, column): load_image(root, f"background_{vertical}_{horizontal}")
            for row, vertical in enumerate(("top", "middle", "bottom"))
            for column, horizontal in enumerate(("left", "center", "right"))
        }
        self.image = tk.PhotoImage(master=root)
        self.size = None

    def resize(self, width, height):
        """Assemble the nine assets into one background matching the window size."""
        self.image.configure(width=width, height=height)
        corner = self.fragments[0, 0]
        # Normally corners keep their native dimensions. Clamp them for the
        # tiny initial window before layout establishes the application's size.
        edge_width = min(corner.width(), width // 2)
        edge_height = min(corner.height(), height // 2)
        xs = (0, edge_width, width - edge_width, width)
        ys = (0, edge_height, height - edge_height, height)
        # These boundaries leave only the middle row/column to absorb resizing:
        # edges stretch along one axis, the center along both, and corners neither.
        for (row, column), fragment in self.fragments.items():
            w = xs[column + 1] - xs[column]
            h = ys[row + 1] - ys[row]
            if w and h:
                scaled = scale_fragment(self.root, fragment, w, h)
                self.image.tk.call(str(self.image), "copy", str(scaled),
                                   "-to", xs[column], ys[row])
        self.size = (width, height)
