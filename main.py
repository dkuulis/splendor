"""Entry point for the Splendor application."""

import argparse
import tkinter as tk

from app import App
from ai import STRATEGIES
from game.initialize import create_initial_state


def main():
    parser = argparse.ArgumentParser(description="Play Splendor against the computer or in manual mode.")
    parser.add_argument("--ai", choices=("manual", *STRATEGIES), default="greedy", help="Computer strategy (default: greedy); manual controls both players")
    args = parser.parse_args()

    strategy = None if args.ai == "manual" else STRATEGIES[args.ai]()

    root = tk.Tk()
    App(root, create_initial_state(), strategy)
    root.mainloop()


if __name__ == "__main__":
    main()
