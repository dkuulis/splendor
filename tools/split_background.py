"""Split background artwork into nine runtime PNGs (requires Pillow)."""

import argparse
from pathlib import Path

from PIL import Image


def split_background(source, destination, corner_size):
    with Image.open(source) as artwork:
        image = artwork.convert("RGB")
    width, height = image.size
    if corner_size <= 0 or 2 * corner_size >= min(width, height):
        raise ValueError("Corner size must be positive and less than half the image dimensions")
    destination.mkdir(parents=True, exist_ok=True)
    xs = (0, corner_size, width - corner_size, width)
    ys = (0, corner_size, height - corner_size, height)
    for row, vertical in enumerate(("top", "middle", "bottom")):
        for column, horizontal in enumerate(("left", "center", "right")):
            fragment = image.crop((xs[column], ys[row], xs[column + 1], ys[row + 1]))
            fragment.save(destination / f"background_{vertical}_{horizontal}.png", optimize=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--corner-size", type=int, default=260)
    args = parser.parse_args()
    try:
        split_background(args.input, args.output, args.corner_size)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Error: {error}\n")


if __name__ == "__main__":
    main()
