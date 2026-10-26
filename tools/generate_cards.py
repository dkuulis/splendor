"""Compose 150×210 card assets from artwork, gems, and game card definitions.

Requires Pillow and a Forum font file. The regular font receives a synthetic
bold treatment to match the existing assets.
"""

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
# Allow direct execution from tools/ while importing the project's game package.
sys.path.insert(0, str(ROOT))

from game.initialize import create_decks
from game.constants import TOKENS

# Compose at eight times the displayed size so text, curves, and gem edges
# remain smooth after downsampling. Layout coordinates below use base pixels;
# Pillow stroke widths and filter sizes are already in high-resolution pixels.
SCALE = 8
SIZE = (150 * SCALE, 210 * SCALE)
PALETTE = {'Diamond': '#e5e7eb', 'Sapphire': '#2563eb', 'Emerald': '#15803d', 'Ruby': '#be123c', 'Onyx': '#334155'}
COST_TEXT = {token: "white" for token in TOKENS}
COST_TEXT["Diamond"] = "#111827"


def generate_cards(cards, artwork_dir, output, font_path, high_res=None):
    fonts = {size: ImageFont.truetype(str(font_path), size * SCALE) for size in (16, 48)}
    output.mkdir(parents=True, exist_ok=True)
    if high_res:
        high_res.mkdir(parents=True, exist_ok=True)

    # Cache by filename so cards can share common artwork or use their own.
    backgrounds = {}

    # Prepare a reusable, card-sized transparent gem overlay for each token type.
    gems = {}
    for token in {card.token for card in cards}:
        with Image.open(artwork_dir / f"{token.lower()}.webp") as original:
            gem = original.convert("RGBA")
        if gem.getchannel("A").getbbox() is None:
            raise ValueError(f"{token} gem is fully transparent.")
        # The alpha bounding box trims transparent margins. contain() fits the
        # cropped gem inside 42×42 without stretching its aspect ratio.
        gem = ImageOps.contain(gem.crop(gem.getchannel('A').getbbox()), (42 * SCALE, 42 * SCALE), Image.Resampling.LANCZOS)
        layer = Image.new('RGBA', SIZE)
        # 102 = card width 150 - right margin 6 - gem box width 42.
        # alpha_composite blends using opacity instead of replacing the background.
        layer.alpha_composite(gem, (102 * SCALE, 6 * SCALE))
        rim = Image.new('RGBA', SIZE, '#f6eedc')
        # MaxFilter(17) expands the alpha mask by 8 high-res pixels on each side
        # (one displayed pixel). putalpha applies that mask to the ivory layer;
        # drawing the original gem on top leaves only the expanded rim visible.
        rim.putalpha(layer.getchannel('A').filter(ImageFilter.MaxFilter(17)))
        gems[token] = Image.alpha_composite(rim, layer)

    for card in cards:
        # IDs begin with card_<nnn>; omit the cost suffix for artwork lookup.
        number = card.id.split("_")[1]

        artwork = artwork_dir / f"card_{number}_l{card.tier}_{card.token.lower()}.webp"
        if not artwork.is_file():
            artwork = artwork_dir / f"card_l{card.tier}_{card.token.lower()}.webp"

        if artwork not in backgrounds:
            # RGBA provides opacity for overlays. LANCZOS blends neighboring
            # pixels to preserve detail and smooth edges when resizing.
            with Image.open(artwork) as original:
                backgrounds[artwork] = original.convert("RGBA").resize(SIZE, Image.Resampling.LANCZOS)

        # Start a fresh composition; shared backgrounds and gem layers stay intact.
        im = Image.alpha_composite(backgrounds[artwork], gems[card.token])
        draw = ImageDraw.Draw(im)

        if card.points:
            position = (6 * SCALE, 12 * SCALE)
            # 'lt' anchors the text's visible top-left at the supplied position.
            # First draw a dark outline, then a narrower white stroke to give
            # Forum Regular a synthetic bold face. Zero points are omitted.
            draw.text(position, str(card.points), font=fonts[48], fill='white', anchor='lt', stroke_width=9, stroke_fill='#25394e')
            draw.text(position, str(card.points), font=fonts[48], fill='white', anchor='lt', stroke_width=4, stroke_fill='white')

        # Follow canonical gem order, skipping zero costs regardless of dict order.
        costs = [(token, card.cost[token]) for token in TOKENS if card.cost.get(token, 0)]
        for index, (token, amount) in enumerate(costs):
            # Bottom-align the column: last circle starts at y=180; preceding
            # circles step upward by 30px (26px diameter plus a 4px gap).
            y = 180 - (len(costs) - 1 - index) * 30
            ink = COST_TEXT[token]
            # Ellipse bounds describe a 26×26 circle, with center (19, y+13).
            draw.ellipse((6 * SCALE, y * SCALE, 32 * SCALE, (y + 26) * SCALE), fill=PALETTE[token], outline='#c5b58d', width=SCALE)
            # 'mm' anchors text at its horizontal and vertical middle.
            draw.text((19 * SCALE, (y + 13) * SCALE), str(amount), font=fonts[16], fill=ink, anchor='mm', stroke_width=2, stroke_fill=ink)

        # Downsample only after all overlays are composed; optionally retain the
        # full 1200×1680 composition in a separate folder under the same card ID.
        asset = im.resize((150, 210), Image.Resampling.LANCZOS)
        path = output / f'{card.id}.png'
        asset.save(path)
        print(f"{artwork} -> {path}")
        if high_res:
            high_res_path = high_res / f"{card.id}.png"
            im.save(high_res_path)
            print(f"{artwork} -> {high_res_path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artwork", type=Path, nargs="?", default=ROOT / "artwork", help="Folder containing card and gem WebP originals (default: artwork)")
    parser.add_argument("output", type=Path, nargs="?", default=ROOT / "assets", help="Destination folder for 150×210 PNG assets (default: assets)")
    parser.add_argument("--font", type=Path, default=ROOT / "assets" / "Forum-Regular.ttf", help="Font file (default: bundled assets/Forum-Regular.ttf)")
    parser.add_argument("--card", type=int, choices=range(1, 91), metavar="1-90", help="Generate only this card number; default: all cards")
    parser.add_argument("--high-res", type=Path, help="Also save 1200×1680 cards in this folder")
    args = parser.parse_args()
    # Deck definitions preserve the original numbered card order across tiers.
    cards = [card for deck in create_decks() for card in deck]
    if args.card:
        cards = [cards[args.card - 1]]
    try:
        if args.high_res and args.high_res.resolve() == args.output.resolve():
            raise ValueError("High-resolution and asset output folders must differ.")
        generate_cards(cards, args.artwork, args.output, args.font, args.high_res)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Error: {error}\n")
    print(f"Generated {len(cards)} card assets in {args.output}")


if __name__ == "__main__":
    main()
