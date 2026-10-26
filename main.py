"""Entry point for the Splendour Tkinter application."""

import tkinter as tk
import sys
from tkinter import ttk


def main() -> None:
    if sys.platform == "darwin" and tk.TkVersion < 8.6:
        raise SystemExit(
            "This app requires Tk 8.6 or newer on macOS. "
            "Apple's system Tk 8.5 can render blank windows. "
            "Use the Homebrew Python environment described in README.md."
        )

    root = tk.Tk()
    root.title("Splendour")
    root.geometry("640x400")
    root.minsize(320, 200)

    frame = ttk.Frame(root, padding=24)
    frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(frame, text="Welcome to Splendour", font=("Helvetica", 20)).pack(
        pady=(0, 16)
    )
    ttk.Label(frame, text="Your Tkinter application is ready.").pack()
    ttk.Button(frame, text="Close", command=root.destroy).pack(pady=24)

    root.mainloop()


if __name__ == "__main__":
    main()
