import tkinter as tk
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"


def load_image(master, name):
    # Cache on the Tk root so images are shared only within their interpreter.
    root = master._root()
    if not hasattr(root, "_splendor_images"):
        root._splendor_images = {}
    if name not in root._splendor_images:
        root._splendor_images[name] = tk.PhotoImage(master=root, file=str(ASSETS / f"{name}.png"))
    return root._splendor_images[name]


class ImageSizes(dict):
    """Lazily measure assets once, without coupling layout to Tk."""

    def __init__(self, master):
        super().__init__()
        self.master = master

    def __missing__(self, name):
        image = load_image(self.master, name)
        size = (image.width(), image.height())
        self[name] = size
        return size
