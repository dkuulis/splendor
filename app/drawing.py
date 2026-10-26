"""Shared geometry for canvas gems."""

from math import cos, pi, sin

from .styles import OUTLINE_PALETTE, PALETTE


def row_centers(count, width, spacing):
    start = (width - (count - 1) * spacing) / 2
    return [start + index * spacing for index in range(count)]


def draw_gem(canvas, color, x, y, radius, **options):
    points = []
    for vertex in range(7):
        angle = vertex * 2 * pi / 7 - pi / 2
        points.extend((x + radius * cos(angle), y + radius * sin(angle)))
    options = {"fill": PALETTE[color], "outline": OUTLINE_PALETTE[color], **options}
    return canvas.create_polygon(*points, **options)


def draw_cost(canvas, color, x, y, radius, **options):
    options = {"fill": PALETTE[color], "outline": OUTLINE_PALETTE[color], **options}
    return canvas.create_oval(
        x - radius, y - radius, x + radius, y + radius,
        **options,
    )
