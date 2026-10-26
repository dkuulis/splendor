"""Downsize a token pile while keeping each token about 60px across (requires Pillow)."""

import argparse
from pathlib import Path

from PIL import Image

# Support both direct script execution and package imports.
if __package__:
    from .image_utils import load_cropped_rgba
else:
    from image_utils import load_cropped_rgba


TOKEN_SIZE = 60
PADDING = 2


def resize_pile(source, destination, token_diameter):
    if token_diameter <= 0:
        raise ValueError("Token diameter must be positive.")
    cropped = load_cropped_rgba(source)

    # Scale by a complete coin's source diameter, not the whole pile's width
    # or the exposed part of an overlapping coin. Larger piles stay larger.
    size = tuple(max(1, round(length * TOKEN_SIZE / token_diameter))
                 for length in cropped.size)
    # Lanczos averages neighboring pixels for smooth edges when downsampling.
    resized = cropped.resize(size, Image.Resampling.LANCZOS)
    output = Image.new("RGBA", (size[0] + 2 * PADDING, size[1] + 2 * PADDING))
    output.alpha_composite(resized, (PADDING, PADDING))
    output.save(destination, format="PNG")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Transparent source PNG or WebP")
    parser.add_argument("output", type=Path, help="Destination PNG path")
    parser.add_argument("--token-diameter", type=int, required=True,
                        help="Complete single-token diameter in source pixels (including hidden parts)")
    args = parser.parse_args()
    try:
        resize_pile(args.input, args.output, args.token_diameter)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Error: {error}\n")


if __name__ == "__main__":
    main()
