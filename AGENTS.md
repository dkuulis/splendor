# Project overview

Splendour is a two-player desktop game built with Python, Tkinter, and ttk.
The human starts; the computer can use manual control or AI.

`RULES.md` describes the simplified rules; do not introduce full Splendor rules without a request.

## Setup and commands

- Use the project `.venv` when available. The application needs Python 3.9+
  with Tkinter; it has no third-party runtime dependencies.
- Create an environment with `python3 -m venv .venv`.
- Launch: `.venv/bin/python main.py`.
- Run tests: `.venv/bin/python -m unittest discover -s tests`.
- Check whitespace: `git diff --check`.
- Check Tk support: `.venv/bin/python -m tkinter`.
- On macOS, use a Python installation with modern Tk. The setup documented
  in README uses Homebrew `python@3.13` and `python-tk@3.13`; Apple's old
  system Tk can produce blank windows. GUI smoke checks need window-server
  access and may fail inside a sandbox even when the code is valid.
- Asset tools additionally require Pillow: `python -m pip install Pillow`
  in the environment used to run those tools.

## Structure and responsibilities

- `main.py`: creates Tk and explicitly passes `create_initial_state()` to App.
- `game/`: plain Python model objects, legal actions, turn transitions, and
  initialization. Keep this package independent of Tkinter.
- `game/initialize.py`: all 90 card definitions and shuffled initial setup.
- `ai/`: strategies implementing `play_turn(state)`. Each performs one legal
  action through State. Register strategies in `ai/__init__.py`.
- `app/app.py`: assembles panels, dispatches actions, refreshes the UI, and
  schedules/cancels AI callbacks. AI currently runs on the UI thread; keep
  strategies quick and preserve cancellation when changing mode/new game.
- Other `app/` modules implement market, card, deck, player, score, header, supply, selection
  and log controls. Keep shared visual constants in `app/styles.py`.
- `tests/`: standard-library unittest coverage for actions and AI.
- `tools/`: optional command-line artwork conversion and asset generation.

## Game model conventions

- Prefer simple objects, dictionaries, and lists. Do not introduce dataclasses
  or typing imports for these models. Keep abstractions small and direct.
- `TOKENS` in `game/constants.py` defines canonical order. Use it for
  rendering, costs, selections, and log output.
- `State.supply` contains available token counts;
- `Player.tokens` contains holdings.
- `State.selected_tokens` contains pending counts, currently one per selected
  type. Selection does not change supply until `take_tokens()` succeeds.
  Finishing a turn clears selection.
- Missing dictionary entries mean zero.
- `Card.token` identifies its permanent discount type. `Card.cost` is a token
  count dictionary. `Player.cards` is keyed by card ID; points and discounts
  are derived from owned cards.
- `State.market` and `State.decks` always contain tiers 1, 2, and 3, with empty
  lists for exhausted tiers.
- `State.log` is a list of action messages rendered by the log panel.

## Artwork and assets

- `images/`: high-resolution originals and previews, ignored by Git.
- `artwork/`: tracked quality-80 WebP source artwork. Preserve alpha for
  tokens, piles, and overlays; card/deck backgrounds may use RGB.
- `assets/`: runtime PNGs, Forum font/license, and generation prompts.
- Card assets are 150×210; card IDs match asset filenames without extensions.
  The generator prefers `card_<nnn>_l<level>_<token>.webp`, falling back to
  `card_l<level>_<token>.webp`.
- Single token assets are 60×60. Pile assets retain approximately 60px per
  token, not per entire image. Names are `<token>.png` for one and
  `<token><count>.png` for multiple; gems support 2–7, gold 2–5.
- `artwork/gems.txt` and `artwork/golds.txt` record complete source-token
  diameters for resizing.
- Retain Python references to displayed Tk PhotoImage objects. A list of
  current images is sufficient.

Example asset commands (run with a Pillow-enabled Python):

```sh
python tools/convert_artwork.py images artwork
python tools/convert_artwork.py images artwork --rgba --pattern 'ruby*.png'
python tools/resize_token.py artwork/gold.webp assets/gold.png
python tools/resize_pile.py artwork/diamond2.webp assets/diamond2.png --token-diameter 770
python tools/generate_cards.py artwork assets --card 78
```

Conversion and generation tools replace matching outputs. Use a temporary
output directory for smoke checks, and regenerate only requested assets.

## Working conventions

- Keep changes focused and preserve unrelated user edits.
- Prefer straightforward functions and loops over extra wrapper classes or
  defensive guards around established model invariants.
- Run relevant unit tests for logic changes. For UI changes, also check Tk
  construction, callbacks, and the affected layout where possible.
- Add comments for rare/obscure library calls/parameters/options.
