import tkinter as tk
from tkinter import ttk

from .styles import LOG_FONT, MUTED_TEXT_COLOR, TABLE_BACKGROUND


class Log(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, background=TABLE_BACKGROUND)
        self.items = []
        self.displayed_messages = []
        self.canvas = tk.Canvas(
            self, width=250, height=200, highlightthickness=0, borderwidth=0,
            background=TABLE_BACKGROUND,
        )
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.on_scroll)
        self.scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)
        self.canvas.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        self.canvas.bind("<Configure>", self.resize_messages)

    def on_scroll(self, first, last):
        self.scrollbar.set(first, last)
        # Text scrolls in canvas coordinates; the tabletop stays fixed to the
        # viewport so its texture continues to line up with neighboring panels.
        self.canvas.coords("background", self.canvas.canvasx(0), self.canvas.canvasy(0))

    def resize_messages(self, event):
        self.update_scroll_region()

    def update_scroll_region(self):
        width = self.canvas.winfo_width()
        if width <= 1:
            width = self.canvas.winfo_reqwidth()
        y = 0
        for item in self.items[:len(self.displayed_messages)]:
            self.canvas.itemconfigure(item, width=max(1, width - 12))
            self.canvas.coords(item, 6, y)
            y = self.canvas.bbox(item)[3] + 12
        # Exclude the background item from scroll bounds: it moves with the
        # viewport, and must never extend the message history's scroll range.
        height = max(self.canvas.winfo_height(), y)
        self.canvas.configure(scrollregion=(0, 0, width, height))

    def refresh(self, messages):
        if self.displayed_messages == messages:
            return
        appended = messages[:len(self.displayed_messages)] == self.displayed_messages
        follow_latest = not appended or not self.displayed_messages or self.canvas.yview()[1] >= 0.999
        top = self.canvas.canvasy(0)
        for index, message in enumerate(messages):
            if index == len(self.items):
                self.items.append(self.canvas.create_text(
                    6, 0, text=message, font=LOG_FONT, fill=MUTED_TEXT_COLOR,
                    justify="left", anchor="nw",
                ))
            elif index >= len(self.displayed_messages) or message != self.displayed_messages[index]:
                self.canvas.itemconfigure(self.items[index], text=message, state="normal")
        for item in self.items[len(messages):]:
            self.canvas.itemconfigure(item, state="hidden")
        self.displayed_messages = list(messages)
        self.update_scroll_region()
        if follow_latest:
            self.canvas.yview_moveto(1)
        else:
            height = float(self.canvas.cget("scrollregion").split()[3])
            self.canvas.yview_moveto(top / height)
