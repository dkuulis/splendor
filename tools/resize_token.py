"""Resize a gem or gold WebP image to a transparent 60×60 PNG (requires Pillow)."""

import argparse
from pathlib import Path

from PIL import Image, ImageOps


def resize_token(source, destination):
    with Image.open(source) as original:
        image = original.convert("RGBA")
    bounds = image.getchannel("A").point(lambda alpha: 255 if alpha > 8 else 0).getbbox()
    if bounds is None:
        raise ValueError("Input image is fully transparent.")
    sprite = ImageOps.contain(image.crop(bounds), (60, 60), Image.Resampling.LANCZOS)
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
