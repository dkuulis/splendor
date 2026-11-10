"""Own game interaction and render it on a single root Canvas."""

import tkinter as tk

from game.initialize import create_initial_state
from game.selection import Selection
from .assets import ImageSizes
from .layout import layout
from .renderer import Renderer
from .styles import TABLE_BACKGROUND

AI_DELAY_MS = 500


class App:
    def __init__(self, root, state, strategy):
        self.root = root
        self.state = state
        self.selection = Selection()
        self.strategy = strategy
        self.state.players[1].is_ai = strategy is not None
        self.pending_ai = None
        self.pending_layout = None
        self.minimum = None
        root.title("Splendor")
        root.configure(background=TABLE_BACKGROUND)
        self.canvas = tk.Canvas(root, background=TABLE_BACKGROUND,
                                highlightthickness=0, borderwidth=0)
        self.canvas.pack(fill="both", expand=True)
        self.renderer = Renderer(self.canvas, self)
        self.image_sizes = ImageSizes(root)
        self.canvas.bind("<Configure>", self.schedule_layout)
        root.bind("<Destroy>", self.on_destroy, add="+")
        self.refresh()

    def schedule_layout(self, event=None):
        if self.pending_layout is None:
            self.pending_layout = self.root.after_idle(self.render)

    def render(self):
        if self.pending_layout is not None:
            self.root.after_cancel(self.pending_layout)
            self.pending_layout = None
        elements, minimum = layout(self.state, self.selection,
                                   self.canvas.winfo_width(), self.canvas.winfo_height(),
                                   self.image_sizes, self.manual_turn)
        if self.minimum != minimum:
            self.minimum = minimum
            self.root.minsize(*minimum)
            self.root.geometry(f"{max(minimum[0], self.root.winfo_width())}x"
                               f"{max(minimum[1], self.root.winfo_height())}")
        self.renderer.render(elements)

    def refresh(self):
        self.cancel_ai()
        self.render()
        if self.ai_turn:
            self.pending_ai = self.root.after(AI_DELAY_MS, self.perform_ai_selection)

    def refresh_selection(self):
        self.render()

    @property
    def ai_turn(self):
        return not self.state.turn.finished and self.state.current_player.is_ai and self.strategy is not None

    @property
    def manual_turn(self):
        return not self.state.turn.finished and not self.ai_turn

    def cancel_ai(self):
        if self.pending_ai is not None:
            self.root.after_cancel(self.pending_ai)
            self.pending_ai = None

    def perform_ai_selection(self):
        self.pending_ai = None
        if not self.ai_turn:
            return
        self.strategy.make_selection(self.state, self.selection)
        self.refresh_selection()
        self.pending_ai = self.root.after(AI_DELAY_MS, self.perform_ai_action)

    def perform_ai_action(self):
        self.pending_ai = None
        if not self.ai_turn:
            return
        self.selection.perform_action(self.state)
        self.refresh()

    def on_destroy(self, event):
        if event.widget is self.root:
            self.cancel_ai()
            if self.pending_layout is not None:
                self.root.after_cancel(self.pending_layout)
                self.pending_layout = None

    def new_game(self):
        self.cancel_ai()
        self.state = create_initial_state()
        self.state.players[1].is_ai = self.strategy is not None
        self.selection = Selection()
        self.refresh()

    def select_card(self, card):
        if self.manual_turn:
            self.selection.select_card(card, self.state)
            self.refresh_selection()

    def select_token(self, token):
        if self.manual_turn:
            self.selection.select_token(token, self.state)
            self.refresh_selection()

    def deselect_token(self, token):
        if self.manual_turn:
            self.selection.deselect_token(token, self.state)
            self.refresh_selection()

    def select_return_token(self, token):
        if self.manual_turn:
            self.selection.select_return_token(token, self.state)
            self.refresh_selection()

    def perform_action(self):
        if not self.manual_turn or not self.selection.can_perform_action(self.state):
            return
        self.selection.perform_action(self.state)
        self.refresh()
