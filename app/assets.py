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
