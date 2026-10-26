from tkinter import ttk

from .styles import (
    MUTED_TEXT_COLOR,
)


class Footer(ttk.Frame):
    def __init__(self, parent, selection_text):
        super().__init__(parent)
        actions = ttk.Frame(self)
        actions.pack(fill="x", pady=(12, 0))
        ttk.Label(actions, textvariable=selection_text).pack(side="left")
        ttk.Button(actions, text="Take selected gems", state="disabled").pack(side="right")
        ttk.Button(actions, text="Pass", state="disabled").pack(side="right", padx=8)

        ttk.Label(self, text="ACTIVITY   •   A new game will appear here once gameplay is connected.", foreground=MUTED_TEXT_COLOR).pack(anchor="w", pady=(14, 0))
