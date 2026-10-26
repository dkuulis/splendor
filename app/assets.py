import tkinter as tk
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"


def load_image(master, name):
    return tk.PhotoImage(master=master, file=str(ASSETS / f"{name}.png"))
