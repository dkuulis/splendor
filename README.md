# Splendor

A two-player Splendor desktop UI using Tkinter and themed `ttk` widgets.

The app starts with shuffled decks and empty player inventories. Choose the
computer strategy at launch with `--ai` (default: `greedy`):

```sh
.venv/bin/python main.py --ai greedy
.venv/bin/python main.py --ai pass-only
.venv/bin/python main.py --ai manual
```

Pass ends the turn without collecting when nothing is selected; two consecutive passes end
the game using score and card-count tie-breaks.
Select one to three different gems, or two of one color when at least four of
that color are in supply, and use Take to collect them. Both options must keep
your inventory at or below 10 tokens. The button is
disabled when the selection is invalid.
The selection panel has one action button and a separate Restart button.
The action button shows Buy, Reserve, Take, or Pass to match the selection.
When the game finishes, it shows a disabled Win, Loose, or Tie from your
perspective. Restart remains available and restores the normal action button.
At game end, the winner's divider stays highlighted with gold laurels beside
the score plaque. A draw leaves both dividers inactive without laurels.
The 10-gem inventory limit is enforced. Click any market card to move it into
the selection panel; click it again to deselect it. Buy is enabled only when
you have enough gems after owned-card discounts, using owned gold as a wildcard
for missing colors. Buying spends matching gems first and returns the actual
gem and gold payment to the bank.
Reservation takes a market card and one gold, subject to the three-reservation
and 10-token limits. Reserved cards appear in the last player-panel block.
Purchases update scores, replace market cards, and trigger the final round at
15 points. Manual lets you control both players. Pass-only AI automatically
passes on the computer's turn. Restart with a different `--ai` value to change
modes. New game preserves the selected strategy and cancels any pending AI action.
The computer displays its selection for half a second before executing it.
Manual controls remain disabled during both AI stages; Restart cancels either stage.

Greedy AI buys the highest-point affordable card, breaking equal-point ties by
the fewest gems spent after discounts. Otherwise, it collects up to three
different needed gems toward the card requiring the fewest collection turns
(at most three gems per turn and one per color), breaking ties by missing gem
count. It prioritizes colors with the lowest available bank count and fills
spare picks from the next-ranked cards without repeating colors.
Cards with no needed gems available
are skipped. Collection respects the inventory limit; if no purchase or useful
collection is possible, it passes.

## Selection rules

Selections are pending choices: they do not transfer tokens or cards until
the action is confirmed. App owns `state` and `selection` separately;
`selection_panel` is the widget that displays pending choices.
`game/selection.py` owns the selection decisions; the UI delegates clicks to it.

1. **Select a colored gem:** clear the selected card and gold, keep other
   selected colored gems, and add one gem of this color. Selecting the same
   color again adds another gem, up to the available supply. Selected gems
   appear as one pile per color.
2. **Select a market card:** replace the selected card and clear all selected
   tokens, including gold. If the new card is affordable, select it for Buy.
   Otherwise, automatically add one gold and select it for Reserve.
3. **Select a reserved card:** only affordable cards belonging to the current
   player can be selected. Replace the selected card and clear all selected
   tokens. An unaffordable reserved card leaves the selection unchanged.
4. **Select gold:** only allowed when an affordable market card is selected
   and gold is available in the bank. Keep the card and select one gold for
   Reserve. Repeated clicks add gold up to the available supply; Reserve is
   enabled only with exactly one selected gold.
5. **Deselect a colored gem:** click its selected pile to remove one gem,
   keeping the rest of that pile and any other selected gems.
6. **Deselect gold:** only allowed when the selected market card is affordable.
   Remove one gold at a time; removing the last gold keeps the card for Buy.
   An unaffordable market card must
   retain gold and remain a reservation.
7. **Deselect a market or reserved card:** click the selected card again to
   clear the card and all selected tokens, including reservation gold.

The action button derives its action from the pending selection:

- Nothing selected: **Pass**.
- Gold selected with a market card: **Reserve**.
- A market or reserved card selected without gold: **Buy**.
- Colored gems selected without a card: **Take**.

Unavailable tokens and cards cannot be selected. Deselecting an absent item
does nothing. Selection changes are disabled after the game ends. Confirming
an action through Selection dispatch clears the selection. Restart creates a
fresh state and selection while keeping the existing widgets.

Selection changes and action confirmation have separate permissions. For example,
an unaffordable market card still selects Reserve when the bank has no gold or reservation
limits are reached; confirmation stays disabled. `Selection.can_select_card`,
`can_select_token`, and `can_deselect_token` return booleans for interaction
availability. `can_perform_action` checks the current action through
`can_buy_card`, `can_reserve_card`, `can_take_tokens`, or `can_pass_turn`, using
the supplied game state. `Selection.perform_action(state)` dispatches the
selected action to `buy_card(card)`, `reserve_card(card)`, `take_tokens(tokens)`,
or `pass_turn()` in `game/state.py`, passing the pending card or tokens directly.
The UI uses these permissions to enable controls. Dispatch and State's action
methods execute without validation; callers must choose an allowed action before
executing it.

## Adding AI strategies

Add a strategy class under `ai/` with `make_selection(state, selection)`. Clear
pending choices and prepare one legal selection using the supplied state;
leave it empty to choose Pass. Strategies do not change State or execute actions.
App displays the selection, then dispatches the action once in a delayed callback.
Register the command-line name and class in `ai/__init__.py`; `--ai` uses this
registry automatically.
Strategies should run quickly because they execute on the UI thread; a future
search-based AI will need background execution.

## Background assets

The app loads nine `assets/background_<row>_<column>.png` fragments separately.
Corners retain their native size; the edges and center stretch to fill the window.
To regenerate the fragments from artwork with Pillow installed:

```sh
python tools/split_background.py artwork/background.webp assets --corner-size 260
```

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

## Generating button assets

The action button uses the 140×120 assets with suffix `2`; Restart keeps its
original 140×42 assets. The action button sits at the top of the 210-pixel
selection area and Restart sits at the bottom.

Regenerate the tall buttons from the matching WebP sources with Pillow:

```sh
.venv/bin/python tools/generate_buttons.py --variant 2 --preview images/buttons_preview2.png
```

Without `--variant 2`, the tool generates the original small buttons. Use
`--buttons restart` to regenerate only Restart. Matching outputs are overwritten.
Return assets are available in both sizes and reuse Take's maroon artwork;
generate them with `--buttons return`, adding `--variant 2` for the tall version.
Disabled result assets are also available in both sizes: `Win` has gold letters,
`Loose` has silver letters, and `Tie` uses the usual disabled label color.
Generate them with `--buttons win loose tie`, adding `--variant 2` for tall assets.

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
