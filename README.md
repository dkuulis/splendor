# Splendor

A two-player Splendor desktop UI using Tkinter and themed `ttk` widgets.

The app starts with shuffled decks and empty player inventories. The Computer
dropdown switches between Manual, Pass-only AI, and Greedy AI (the default).
Go! passes when no gems are selected; two consecutive passes end
the game using score and card-count tie-breaks. The log records actual actions.
Select one to three different gems and use Go! to collect them. The button is
disabled when the selection is invalid.
The 10-gem inventory limit is enforced. Click anywhere on an affordable market
card to buy it, applying owned-card discounts and returning payment to the bank.
Purchases update scores, replace market cards, and trigger the final round at
15 points. Manual lets you control both players. Pass-only AI automatically
passes on the computer's turn. You can switch modes at any time; switching to
Manual cancels a pending AI action. New game preserves the selected mode.

Greedy AI buys the highest-point affordable card, breaking equal-point ties by
the fewest gems spent after discounts. Otherwise, it collects up to three
different needed gems toward the card requiring the fewest collection turns
(at most three gems per turn and one per color), breaking ties by missing gem
count. It prioritizes colors with the lowest available bank count and fills
spare picks from the next-ranked cards without repeating colors.
Cards with no needed gems available
are skipped. Collection respects the inventory limit; if no purchase or useful
collection is possible, it passes.

## Adding AI strategies

Add a strategy class under `ai/` with `play_turn(state)`, performing exactly
one legal action through the state's methods, then register its display name
and class in `ai/__init__.py`. The dropdown uses this registry automatically.
Strategies should run quickly because they execute on the UI thread; a future
search-based AI will need background execution.

## Resizing token assets

The optional asset tool requires Pillow (`python -m pip install Pillow`). It
crops transparent margins, preserves proportions, and writes a centered,
transparent 60×60 PNG:

```sh
python tools/resize_token.py artwork/gold.webp assets/gold.png
```

## Generating card assets

Compress original card and deck artwork with the optional Pillow-based tool:

```sh
python tools/convert_artwork.py images artwork
```

It converts every `card*.png` and `deck*.png` in the source folder to WebP
at quality 80, drops alpha, and preserves dimensions and base filenames.
Original PNGs remain unchanged; matching destination files are replaced.

Use `--rgba` to preserve transparency and repeat `--pattern` to select other
files. WebP color remains lossy at quality 80; alpha is preserved losslessly.

```sh
python tools/convert_artwork.py images artwork --rgba \
  --pattern diamond.png --pattern sapphire.png --pattern emerald.png \
  --pattern ruby.png --pattern onyx.png --pattern gold.png --pattern 'disabled*.png'
```

With Pillow installed, compose all 90 cards from the high-resolution artwork
and gem WebP files in `artwork`, using attributes from `game/initialize.py`:

```sh
python tools/generate_cards.py artwork assets
```

The input folder must contain `<gem>.webp` icons (lowercase gem names).
For artwork, the tool first looks for `card_<nnn>_l<level>_<gem>.webp`
(for example, `card_068_l2_ruby.webp`), then falls back to
`card_l<level>_<gem>.webp`. It logs the artwork path and output path for each
generated file. Output is fixed at 150×210px, using
card IDs as filenames. Existing output files are replaced. The Forum font
uses synthetic bold to match the current assets.

Use `--card 78` to render one card, and `--high-res images/cards` to also save
1200×1680 versions. Input and output default to `artwork` and `assets`; the
bundled `font/Forum-Regular.ttf` is used unless overridden with `--font`.
The `images` folder is ignored by Git.

## Setup


On macOS, use Homebrew Python with a modern Tk. Apple's system Python uses
an obsolete Tk 8.5 that can display blank windows.

```sh
brew install python@3.13 python-tk@3.13
/opt/homebrew/bin/python3.13 -m venv .venv
source .venv/bin/activate
python main.py
```

The path above is for Apple Silicon; on Intel Macs use
`/usr/local/bin/python3.13`. If `.venv` was created with Apple's Python,
rename it to `.venv-old` before creating the new environment.

### Other platforms

Requires Python 3.9 or newer with Tkinter support. Tkinter is provided by
your Python installation, so there are no third-party dependencies to install.

```sh
python3 -m venv .venv
source .venv/bin/activate
python main.py
```

On Windows, activate the environment with `.venv\Scripts\activate` instead.

You can also run directly without activating the environment:

```sh
.venv/bin/python main.py
```

To check that your Python installation includes Tkinter, run
`python -m tkinter`; a small demonstration window should appear.
