"""Split original divider PNGs into artwork and runtime tiles (requires Pillow)."""

import argparse
from pathlib import Path

from PIL import Image


def split_dividers(source, artwork, assets):
    artwork.mkdir(parents=True, exist_ok=True)
    assets.mkdir(parents=True, exist_ok=True)
    # These crops isolate the end caps and an uninterrupted rail from the
    # 2172×724 originals, excluding the central ornament and vertical margins.
    sections = (("left", 0, 174, 96), ("middle", 362, 594, 128),
                ("right", 1998, 2172, 96))
    tiles = {}
    for state in ("active", "inactive"):
        with Image.open(source / f"divider_{state}.png") as original:
            image = original.convert("RGBA")
        for section, left, right, width in sections:
            name = f"divider_{state}_{section}"
            fragment = image.crop((left, 307, right, 401))
            fragment.save(artwork / f"{name}.webp", quality=80, method=6)
            with Image.open(artwork / f"{name}.webp") as saved:
                tiles[state, section] = saved.resize((width, 52), Image.Resampling.LANCZOS)

    # Ignore nearly invisible alpha fringes when measuring padding, retaining
    # the original alpha inside the crop. Use shared vertical bounds so all
    # six pieces keep the same height and the assembled rails stay aligned.
    bounds = {key: tile.getchannel("A").point(lambda alpha: 255 if alpha > 8 else 0).getbbox()
              for key, tile in tiles.items()}
    top = min(box[1] for box in bounds.values())
    bottom = max(box[3] for box in bounds.values())
    for (state, section), tile in tiles.items():
        left, _, right, _ = bounds[state, section]
        tile.crop((left, top, right, bottom)).save(
            assets / f"divider_{state}_{section}.png", optimize=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("artwork", type=Path)
    parser.add_argument("assets", type=Path)
    args = parser.parse_args()
    split_dividers(args.input, args.artwork, args.assets)


if __name__ == "__main__":
    main()
