from tkinter import ttk

class Header(ttk.Frame):
    def __init__(self, parent, on_new_game):
        super().__init__(parent)
        self.new_game_button = ttk.Button(self, text="New game", command=on_new_game)
        self.new_game_button.pack(fill="x")
