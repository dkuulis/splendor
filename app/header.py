from tkinter import ttk

class Header(ttk.Frame):
    def __init__(self, parent, on_new_game=None, control=None, control_options=(), on_control_changed=None):
        super().__init__(parent)
        self.new_game_button = ttk.Button(self, text="New game", command=on_new_game, state="normal" if on_new_game else "disabled")
        self.new_game_button.pack(fill="x", pady=(0, 8))
        self.control_dropdown = ttk.Combobox(self, textvariable=control, values=control_options, state="readonly", width=16)
        self.control_dropdown.pack(fill="x")
        if on_control_changed:
            self.control_dropdown.bind("<<ComboboxSelected>>", lambda event: on_control_changed())
