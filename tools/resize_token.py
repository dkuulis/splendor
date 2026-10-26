"""Resize a gem or gold WebP image to a transparent 60×60 PNG (requires Pillow)."""

import argparse
from pathlib import Path

from PIL import Image, ImageOps

# Support both direct script execution and package imports.
if __package__:
    from .image_utils import load_cropped_rgba
else:
    from image_utils import load_cropped_rgba


def resize_token(source, destination):
    cropped = load_cropped_rgba(source)
    sprite = ImageOps.contain(cropped, (60, 60), Image.Resampling.LANCZOS)
    output = Image.new("RGBA", (60, 60))
    output.alpha_composite(sprite, ((60 - sprite.width) // 2, (60 - sprite.height) // 2))
    output.save(destination, format="PNG")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Source WebP, e.g. artwork/gold.webp")
    parser.add_argument("output", type=Path, help="Destination PNG path")
    args = parser.parse_args()
    try:
        resize_token(args.input, args.output)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Error: {error}\n")


if __name__ == "__main__":
    main()
