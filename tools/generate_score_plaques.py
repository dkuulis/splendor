"""Add scores 0–23 to the existing plaque PNGs (requires Pillow)."""

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SCALE = 8
MAX_SCORE = 23
TEXT_COLOR = "#30271f"
PLAQUES = ("score_plaque", "score_plaque_inactive")


def generate_score_plaques(source, output, font_path, preview):
    output.mkdir(parents=True, exist_ok=True)
    font = ImageFont.truetype(str(font_path), 48 * SCALE)
    sheet = Image.new("RGB", (8 * 112, 6 * 94), "#a99b88") if preview else None
    for state, name in enumerate(PLAQUES):
        with Image.open(source / f"{name}.png") as original:
            plaque = original.convert("RGBA")
        for score in range(MAX_SCORE + 1):
            lettering = Image.new("RGBA", (plaque.width * SCALE, plaque.height * SCALE))
            draw = ImageDraw.Draw(lettering)
            label = str(score)
            # A half-pixel stroke supplies synthetic bold for Forum Regular.
            stroke = SCALE // 2
            left, top, right, bottom = draw.textbbox(
                (0, 0), label, font=font, stroke_width=stroke)
            position = ((lettering.width - (right - left)) / 2 - left,
                        (lettering.height - (bottom - top)) / 2 - top)
            draw.text(position, label, font=font, fill=TEXT_COLOR,
                      stroke_width=stroke, stroke_fill=TEXT_COLOR)
            lettering = lettering.resize(plaque.size, Image.Resampling.LANCZOS)
            image = Image.alpha_composite(plaque, lettering)
            image.putalpha(plaque.getchannel("A"))
            image.save(output / f"{name}{score}.png")
            if sheet is not None:
                x = (score % 8) * 112 + 8
                y = (state * 3 + score // 8) * 94 + 8
                sheet.paste(image, (x, y), image)
    if sheet is not None:
        preview.parent.mkdir(parents=True, exist_ok=True)
        sheet.save(preview)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "assets",
                        help="Directory containing the two blank plaque PNGs")
    parser.add_argument("--output", type=Path, default=ROOT / "assets")
    parser.add_argument("--font", type=Path, default=ROOT / "font/Forum-Regular.ttf")
    parser.add_argument("--preview", type=Path,
                        help="Optional sheet with active scores above inactive scores")
    args = parser.parse_args()
    generate_score_plaques(args.source, args.output, args.font, args.preview)


if __name__ == "__main__":
    main()
