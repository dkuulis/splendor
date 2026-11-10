"""Apply layout descriptions to one Canvas while retaining its image items.

Layout owns scene geometry and permissions; Renderer owns Tk objects and event
routing. Each render compares the new scene with the previous one and sends only
changed image properties to Tk. Source artwork is cached by assets.load_image;
this module also retains generated background and divider PhotoImages.
"""

import tkinter as tk

from .assets import load_image
from .background import Background


class Renderer:
    """Keep an item pool for the lifetime of App, including across Restart."""

    def __init__(self, canvas, app):
        self.canvas = canvas
        self.app = app
        # items retains every allocated slot, including currently absent ones.
        # descriptions contains only the current scene, so old actions disappear
        # immediately even though the corresponding Canvas IDs remain reusable.
        self.items = {}
        self.descriptions = {}
        self.images = {}
        self.composite_sizes = {}
        self.background = Background(canvas)
        self.order = ()
        canvas.bind('<Button-1>', self.click)
        canvas.bind('<Motion>', self.motion)
        canvas.bind('<Leave>', lambda event: canvas.configure(cursor=''))

    def image(self, name, size):
        """Resolve cached artwork or rebuild a composite at its requested size.

        Background stretches nine fragments; dividers tile their middle strip
        between fixed end caps. Composite PhotoImages are updated in place and
        retained here because Canvas does not own their Python references.
        """
        if size is None:
            return load_image(self.canvas, name) if name else ''
        if name == 'background':
            if self.background.size != size:
                self.background.resize(*size)
            return self.background.image
        if self.composite_sizes.get(name) != size:
            left, middle, right = [load_image(self.canvas, name + '_' + section)
                                   for section in ('left', 'middle', 'right')]
            if name not in self.images:
                self.images[name] = tk.PhotoImage(master=self.canvas)
            image = self.images[name]
            width, height = size
            image.configure(width=width, height=height)
            image.blank()
            right_x = width - right.width()
            sections = [(left, 0, left.width())]
            sections.extend((middle, x, min(middle.width(), right_x - x))
                            for x in range(left.width(), right_x, middle.width()))
            sections.append((right, right_x, right.width()))
            for tile, x, w in sections:
                # Tcl copy crops the final repeat and retains transparent pixels.
                image.tk.call(str(image), 'copy', str(tile), '-from', 0, 0, w, height, '-to', x, 0)
            self.composite_sizes[name] = size
        return self.images[name]

    def render(self, elements):
        """Reconcile one full scene without deleting items or scheduling AI work."""
        # An absent key releases its visible slot, not its Canvas item. When the
        # key returns it has no previous description and is fully configured.
        for key in self.descriptions.keys() - elements.keys():
            self.canvas.itemconfigure(self.items[key], state='hidden')
        for key, element in elements.items():
            old = self.descriptions.get(key)
            if key not in self.items:
                self.items[key] = self.canvas.create_image(0, 0, anchor='nw', state='hidden')
            item = self.items[key]
            if old is None or (old['x'], old['y']) != (element['x'], element['y']):
                self.canvas.coords(item, element['x'], element['y'])
            # Collect only changed options so unchanged scenes do no item work.
            changes = {}
            if old is None or (old['image'], old['size']) != (element['image'], element['size']):
                changes['image'] = self.image(element['image'], element['size'])
            if old is None or old['visible'] != element['visible']:
                changes['state'] = 'normal' if element['visible'] else 'hidden'
            if changes:
                self.canvas.itemconfigure(item, **changes)
        # Reused items keep their old Canvas stacking order. Restore the layout
        # order when scene membership or ordering changes, including hidden slots.
        order = tuple(sorted(elements, key=lambda key: elements[key]['order']))
        if order != self.order:
            for key in order:
                self.canvas.tag_raise(self.items[key])
            self.order = order
        self.descriptions = elements
        self.canvas.configure(cursor='')

    def current_action(self):
        """Resolve the topmost hovered item against the latest scene.

        Tk's special "current" tag identifies the image under the pointer.
        Looking up its action here avoids per-item callbacks capturing a card
        that has since been replaced. A decorative item with no action blocks
        clicks rather than passing them to an image underneath.
        """
        current = self.canvas.find_withtag('current')
        if not current:
            return None
        for key, element in self.descriptions.items():
            if self.items[key] == current[0] and element['visible']:
                return element['action']
        return None

    def click(self, event):
        action = self.current_action()
        if action:
            name, args = action
            getattr(self.app, name)(*args)

    def motion(self, event):
        self.canvas.configure(cursor='hand2' if self.current_action() else '')
