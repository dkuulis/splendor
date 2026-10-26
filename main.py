"""Entry point for the Splendour application."""

import tkinter as tk

from app import App
from game.preview import create_preview_state


def main():
    root = tk.Tk()
    App(root, create_preview_state())
    root.mainloop()


if __name__ == "__main__":
    main()
