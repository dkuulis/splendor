"""Entry point for the Splendour application."""

import tkinter as tk

from app import App
from game.initialize import create_initial_state


def main():
    root = tk.Tk()
    App(root, create_initial_state())
    root.mainloop()


if __name__ == "__main__":
    main()
