"""Shared geometry for canvas gems and card markers."""

from .styles import OUTLINE_PALETTE, PALETTE


def row_centers(count, width, spacing):
    start = (width - (count - 1) * spacing) / 2
    return [start + index * spacing for index in range(count)]


def draw_gem(canvas, color, x, y, radius, **options):
    options = {"fill": PALETTE[color], "outline": OUTLINE_PALETTE[color], **options}
    return canvas.create_oval(
        x - radius, y - radius, x + radius, y + radius,
        **options,
    )


def draw_card_marker(canvas, color, x, y, size):
    half = size / 2
    return canvas.create_rectangle(
        x - half, y - half, x + half, y + half,
        fill=PALETTE[color], outline=OUTLINE_PALETTE[color],
    )
