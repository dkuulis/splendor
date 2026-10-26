"""Compose button PNGs from enamel artwork (requires Pillow)."""

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SIZE = (140, 42)
SCALE = 8
BUTTONS = ("buy", "reserve", "take", "restart")
RESULT_COLORS = {"win": "#e5bd61", "loose": "#c0c0c0", "tie": "#c9c2b4"}
TOPS = (5, 55, 105, 163)


def generate_buttons(artwork, output, preview, buttons, variant):
    output.mkdir(parents=True, exist_ok=True)
    size = SIZE if variant == 1 else (140, 120)
    suffix = "" if variant == 1 else "2"
    font = ImageFont.truetype(str(ROOT / "font/Forum-Regular.ttf"), 20 * SCALE)
    tops = (TOPS if variant == 1 and tuple(buttons) == BUTTONS else
            tuple(5 + (size[1] + 8) * i for i in range(len(buttons))))
    sheet = Image.new("RGB", (300, tops[-1] + size[1] + 5), "#a99b88")
    for column, state in enumerate(("enabled", "disabled")):
        for name, top in zip(buttons, tops):
            if state == "enabled" and (name == "blank" or name in RESULT_COLORS):
                continue
            artwork_name = "take" if name == "return" else name
            source = f"button_{artwork_name}_enabled" if state == "enabled" else "button_disabled"
            source += suffix
            with Image.open(artwork / f"{source}.webp") as original:
                if original.convert("RGBA").getchannel("A").getextrema() != (255, 255):
                    raise ValueError(f"Button artwork must be fully opaque: {source}")
                image = original.convert("RGB")
            image = image.resize(
                (size[0] * SCALE, size[1] * SCALE), Image.Resampling.LANCZOS)
            if name != "blank":
                draw = ImageDraw.Draw(image)
                label = name.capitalize()
                left, upper, right, lower = draw.textbbox((0, 0), label, font=font)
                position = ((image.width - (right - left)) / 2 - left,
                            (image.height - (lower - upper)) / 2 - upper)
                ink = "#fff0cc" if state == "enabled" else "#c9c2b4"
                if name in RESULT_COLORS:
                    ink = RESULT_COLORS[name]
                draw.text(position, label, font=font, fill=ink)
            image = image.resize(size, Image.Resampling.LANCZOS)
            filename = (f"button_disabled{suffix}.png" if name == "blank" else
                        f"button_{name}_{state}{suffix}.png")
            image.save(output / filename)
            sheet.paste(image, (5 + column * 150, top))
    if preview:
        preview.parent.mkdir(parents=True, exist_ok=True)
        sheet.save(preview)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artwork", type=Path, default=ROOT / "artwork")
    parser.add_argument("--output", type=Path, default=ROOT / "assets")
    parser.add_argument("--preview", type=Path)
    parser.add_argument("--variant", type=int, choices=(1, 2), default=1,
                        help="1: original 140x42 buttons; 2: tall 140x120 action buttons")
    parser.add_argument("--buttons", nargs="+",
                        choices=BUTTONS + ("pass", "return", "blank") + tuple(RESULT_COLORS),
                        help="Only generate these buttons; blank is unlabeled; win, loose, tie are disabled only")
    args = parser.parse_args()
    buttons = args.buttons or (BUTTONS if args.variant == 1 else
                              ("buy", "reserve", "take", "pass", "blank"))
    if args.variant == 2 and "restart" in buttons:
        parser.error("Restart uses the original small variant")
    generate_buttons(args.artwork, args.output, args.preview, buttons, args.variant)


if __name__ == "__main__":
    main()
