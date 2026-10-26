from tkinter import ttk

from .styles import (
    SUBTITLE_FONT,
    TITLE_FONT,
)


class Header(ttk.Frame):
    def __init__(self, parent, player_names, on_new_game=None, control=None, control_options=(), on_control_changed=None):
        super().__init__(parent)
        ttk.Label(self, text="SPLENDOUR", font=TITLE_FONT).pack(side="left")
        ttk.Label(self, text="  vs  ".join(player_names), font=SUBTITLE_FONT).pack(side="left", padx=24)
        ttk.Label(self, text="Computer:").pack(side="left", padx=(0, 6))
        self.control_dropdown = ttk.Combobox(self, textvariable=control, values=control_options, state="readonly", width=16)
        self.control_dropdown.pack(side="left")
        if on_control_changed:
            self.control_dropdown.bind("<<ComboboxSelected>>", lambda event: on_control_changed())
        self.new_game_button = ttk.Button(self, text="New game", command=on_new_game, state="normal" if on_new_game else "disabled")
        self.new_game_button.pack(side="right")
        ttk.Button(self, text="Rules", state="disabled").pack(side="right", padx=8)
