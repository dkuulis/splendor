"""Compose 150×150 noble assets from clean WebP artwork (requires Pillow).

Each noble awards three points; colored squares show owned-card requirements.
Uses the noble IDs, points, and requirements from the game model.
"""

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
# Allow direct execution from tools/ while importing the game package.
sys.path.insert(0, str(ROOT))

from game.constants import DIAMOND, SAPPHIRE, EMERALD, RUBY, ONYX, TOKENS
from game.initialize import create_nobles

SCALE = 8
SIZE = (150 * SCALE, 150 * SCALE)
PALETTE = {
    DIAMOND: "#e5e7eb", SAPPHIRE: "#2563eb", EMERALD: "#15803d",
    RUBY: "#be123c", ONYX: "#334155",
}


def generate_nobles(nobles, artwork_dir, output, font_path, high_res=None):
    if high_res and high_res.resolve() == output.resolve():
        raise ValueError("High-resolution and asset output folders must differ.")
    # images/ holds clean PNG originals with the same stems as the outputs.
    for destination in (output, high_res):
        if destination and destination.resolve() in (artwork_dir.resolve(), (ROOT / "images").resolve()):
            raise ValueError("Use a separate output folder to preserve clean originals.")

    fonts = {size: ImageFont.truetype(str(font_path), size * SCALE) for size in (16, 48)}
    output.mkdir(parents=True, exist_ok=True)
    if high_res:
        high_res.mkdir(parents=True, exist_ok=True)

    for noble in nobles:
        artwork = artwork_dir / f"{noble.id}.webp"
        with Image.open(artwork) as original:
            if original.width != original.height:
                raise ValueError(f"Noble artwork must be square: {artwork}")
            im = original.convert("RGBA").resize(SIZE, Image.Resampling.LANCZOS)
        draw = ImageDraw.Draw(im)

        # 'lt' anchors the visible numeral top-left. Stroke widths are in
        # high-resolution pixels, matching generate_cards.py's synthetic bold.
        position = (6 * SCALE, 12 * SCALE)
        draw.text(position, str(noble.points), font=fonts[48], fill="white", anchor="lt",
                  stroke_width=9, stroke_fill="#25394e")
        draw.text(position, str(noble.points), font=fonts[48], fill="white", anchor="lt",
                  stroke_width=4, stroke_fill="white")

        costs = [(token, noble.requirements[token]) for token in TOKENS
                 if noble.requirements.get(token, 0)]
        for index, (token, amount) in enumerate(costs):
            y = 120 - (len(costs) - 1 - index) * 30
            ink = "#111827" if token == DIAMOND else "white"
            # Pillow rectangle endpoints are inclusive; subtract one pixel
            # so each square is exactly 26×26 base pixels before downsampling.
            draw.rectangle((6 * SCALE, y * SCALE, 32 * SCALE - 1, (y + 26) * SCALE - 1),
                           fill=PALETTE[token], outline="#c5b58d", width=SCALE)
            # 'mm' centers the number horizontally and vertically in its square.
            draw.text((19 * SCALE, (y + 13) * SCALE), str(amount), font=fonts[16],
                      fill=ink, anchor="mm", stroke_width=2, stroke_fill=ink)

        path = output / f"{noble.id}.png"
        im.resize((150, 150), Image.Resampling.LANCZOS).save(path)
        print(f"{artwork} -> {path}")
        if high_res:
            im.save(high_res / f"{noble.id}.png")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artwork", type=Path, nargs="?", default=ROOT / "artwork",
                        help="Folder containing clean noble WebPs (default: artwork)")
    parser.add_argument("output", type=Path, nargs="?", default=ROOT / "assets",
                        help="Destination for 150×150 PNG assets (default: assets)")
    parser.add_argument("--font", type=Path, default=ROOT / "font" / "Forum-Regular.ttf",
                        help="Forum font file (default: bundled Forum-Regular.ttf)")
    parser.add_argument("--noble", type=int, choices=range(1, 11), metavar="1-10",
                        help="Generate only this noble number; default: all ten")
    parser.add_argument("--high-res", type=Path,
                        help="Also save 1200×1200 compositions in a separate folder")
    args = parser.parse_args()
    nobles = create_nobles()
    if args.noble:
        nobles = [nobles[args.noble - 1]]
    try:
        generate_nobles(nobles, args.artwork, args.output, args.font, args.high_res)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Error: {error}\n")
    print(f"Generated {len(nobles)} noble assets in {args.output}")


if __name__ == "__main__":
    main()
