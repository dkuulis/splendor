import tkinter as tk
from tkinter import ttk

from .styles import LOG_FONT, MUTED_TEXT_COLOR


class Log(ttk.LabelFrame):
    def __init__(self, parent, messages):
        super().__init__(parent, text="Log", padding=10)
        self.messages = messages
        self.labels = []
        background = ttk.Style(self).lookup("TFrame", "background") or self.winfo_toplevel().cget("background")
        self.canvas = tk.Canvas(
            self, width=250, height=200, highlightthickness=0, borderwidth=0,
            background=background,
        )
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.content = ttk.Frame(self.canvas)
        self.content_window = self.canvas.create_window(0, 0, window=self.content, anchor="nw")
        self.content.bind("<Configure>", self.update_scroll_region)
        self.canvas.bind("<Configure>", self.resize_messages)

    def resize_messages(self, event):
        self.canvas.itemconfigure(self.content_window, width=event.width)
        for label in self.labels:
            label.configure(wraplength=max(1, event.width - 12))
        self.after_idle(self.update_scroll_region)

    def update_scroll_region(self, event=None):
        height = max(self.canvas.winfo_height(), self.content.winfo_reqheight())
        self.canvas.itemconfigure(self.content_window, height=height)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def refresh(self):
        for label in self.labels:
            label.destroy()
        self.labels.clear()
        for message in self.messages:
            self.create_message(message)
        self.content.update_idletasks()
        self.update_scroll_region()
        self.canvas.yview_moveto(1)

    def create_message(self, message):
        label = ttk.Label(
            self.content, text=message, font=LOG_FONT,
            foreground=MUTED_TEXT_COLOR, justify="left",
            wraplength=max(1, (self.canvas.winfo_width() if self.canvas.winfo_width() > 1 else 250) - 12),
        )
        label.pack(fill="x", anchor="w", padx=6, pady=(0, 12))
        self.labels.append(label)
