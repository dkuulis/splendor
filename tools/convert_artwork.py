"""Convert PNGs to quality-80 WebP, optionally preserving alpha (requires Pillow)."""

import argparse
from pathlib import Path

from PIL import Image


def convert_artwork(source, destination, patterns=("card*.png", "deck*.png"), rgba=False):
    if not source.is_dir():
        raise ValueError(f"Input folder does not exist: {source}")
    files = sorted({path for pattern in patterns for path in source.glob(pattern) if path.is_file()})
    if not files:
        raise ValueError(f"No files matching {', '.join(patterns)} found in {source}")
    destination.mkdir(parents=True, exist_ok=True)
    for path in files:
        output = destination / f"{path.stem}.webp"
        with Image.open(path) as image:
            # RGB drops alpha; RGBA retains it (WebP encodes alpha losslessly).
            # Method 6 uses the slowest encoding setting for better compression.
            image.convert("RGBA" if rgba else "RGB").save(output, format="WEBP", quality=80, method=6)
        print(f"{path} -> {output}")
    return len(files)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, nargs="?", default=Path("images"), help="Source folder (default: images)")
    parser.add_argument("output", type=Path, nargs="?", default=Path("artwork"), help="Destination folder (default: artwork)")
    parser.add_argument("--rgba", action="store_true", help="Preserve transparency instead of dropping alpha")
    parser.add_argument("--pattern", action="append", help="Filename pattern; repeat for multiple patterns (default: card*.png and deck*.png)")
    args = parser.parse_args()
    try:
        count = convert_artwork(args.input, args.output, args.pattern or ("card*.png", "deck*.png"), args.rgba)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Error: {error}\n")
    print(f"Converted {count} images to quality-80 WebP in {args.output}")


if __name__ == "__main__":
    main()
