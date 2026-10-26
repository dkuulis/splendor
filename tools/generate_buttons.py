"""Compose 140×42 button PNGs from enamel artwork (requires Pillow)."""

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SIZE = (140, 42)
SCALE = 8
BUTTONS = ("buy", "reserve", "take", "restart")
TOPS = (5, 55, 105, 163)


def generate_buttons(artwork, output, preview):
    output.mkdir(parents=True, exist_ok=True)
    font = ImageFont.truetype(str(ROOT / "font/Forum-Regular.ttf"), 20 * SCALE)
    sheet = Image.new("RGB", (300, 210), "#a99b88")
    for column, state in enumerate(("enabled", "disabled")):
        for name, top in zip(BUTTONS, TOPS):
            source = f"button_{name}_enabled" if state == "enabled" else "button_disabled"
            with Image.open(artwork / f"{source}.webp") as original:
                if original.convert("RGBA").getchannel("A").getextrema() != (255, 255):
                    raise ValueError(f"Button artwork must be fully opaque: {source}")
                image = original.convert("RGB")
            image = image.resize(
                (SIZE[0] * SCALE, SIZE[1] * SCALE), Image.Resampling.LANCZOS)
            draw = ImageDraw.Draw(image)
            label = name.capitalize()
            left, upper, right, lower = draw.textbbox((0, 0), label, font=font)
            position = ((image.width - (right - left)) / 2 - left,
                        (image.height - (lower - upper)) / 2 - upper)
            ink = "#fff0cc" if state == "enabled" else "#c9c2b4"
            draw.text(position, label, font=font, fill=ink)
            image = image.resize(SIZE, Image.Resampling.LANCZOS)
            image.save(output / f"button_{name}_{state}.png")
            sheet.paste(image, (5 + column * 150, top))
    if preview:
        preview.parent.mkdir(parents=True, exist_ok=True)
        sheet.save(preview)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artwork", type=Path, default=ROOT / "artwork")
    parser.add_argument("--output", type=Path, default=ROOT / "assets")
    parser.add_argument("--preview", type=Path)
    args = parser.parse_args()
    generate_buttons(args.artwork, args.output, args.preview)


if __name__ == "__main__":
    main()
