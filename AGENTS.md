# Project overview

Splendor is a two-player desktop game built with Python, Tkinter, and ttk.
The human starts; `--ai` selects the computer strategy or manual control.
Follow the simplified rules in `RULES.md`; do not introduce full Splendor
rules without a request.

## Setup and checks

- Use the project `.venv` when available. Runtime requires Python 3.9+ with
  Tkinter and no third-party packages. Asset tools additionally need Pillow.
- Setup and platform-specific installation instructions are in `README.md`.
  On macOS, use modern Tk; Apple's old system Tk can produce blank windows.
- Launch: `.venv/bin/python main.py` (defaults to greedy AI).
- Tests: `.venv/bin/python -m unittest discover -s tests`.
- Include GUI tests: `SPLENDOR_GUI_TESTS=1 .venv/bin/python -m unittest discover -s tests`.
  These need window-server access and may fail inside a sandbox.
- Whitespace: `git diff --check`.

## Code responsibilities

- `main.py` creates Tk, the initial state, and the selected AI strategy.
- `game/` contains plain Python models and rules; keep it independent of Tkinter.
  `state.py` owns selection, action validation/execution, and market replacement.
  Keep validation beside its action.
- `player.py` owns holdings and derived points, discounts, capacity, and payment.
  Use these calculations through the relevant player.
- `State.finish_turn()` awards a noble, clears selection, and advances the turn.
  `noble.py` handles awards; `turn.py` handles final rounds, completion, and ties.
  `initialize.py` defines cards, nobles, and shuffled setup.
- `ai/` strategies implement `play_turn(state)` and perform one legal action
  through State. Register them in `ai/__init__.py`.
- `app/app.py` assembles panels, dispatches actions, and schedules AI callbacks.
  AI runs on the UI thread: keep strategies quick and cancel pending callbacks
  on Restart and window destruction.
- `app/selection_panel.py` contains Buy, Reserve, Take, and Restart.
  Take with zero gems ends the turn without collecting.
- `app/divider_panel.py` shows scores and turn/result highlights. A winner
  stays highlighted with laurels; a draw leaves both dividers inactive.
  There is no header, separate score panel, or log panel.
- Keep shared visual constants in `app/styles.py`. Use `app/assets.py` to
  load and cache images; retain Python references to Tk PhotoImage objects.
- Hide exhausted market decks without shifting card alignment; restore them
  when replenished, including on Restart.
- `tests/` uses standard-library unittest; `tools/` contains optional asset tools.

## Model conventions

- Prefer simple objects, dictionaries, and lists. Do not introduce dataclasses
  or typing imports for the models.
- Use `TOKENS` for display, selection, and log ordering. Payment calculations
  can iterate over cost entries directly.
- `State.supply` holds available tokens; `Player.tokens` holds owned tokens.
  Selection is pending and does not transfer tokens. Finishing a turn clears it.
- Missing entries in sparse token/cost/selection dictionaries mean zero.
  Gem keys in `Player.cards` and `Player.discounts`, and tiers 1–3 in
  `State.market` and `State.decks`, are always present; index them directly.
- Discounts derive only from owned cards. Points include cards and nobles.
  Payments use matching gems before gold and include only nonzero amounts.
- Noble requirements count permanent card bonuses, not tokens. Award at most
  the first qualifying available noble each turn, without spending holdings
  or replacing the noble, before checking turn completion.
- `State.log` retains internal action history; it is not displayed.

## Artwork and assets

- `images/`: high-resolution originals and previews, ignored by Git.
- `artwork/`: tracked quality-80 WebP sources. Preserve alpha where needed,
  including tokens, piles, dividers, plaques, and laurels.
- `assets/`: runtime PNGs; `font/`: Forum font and license;
  `prompts/`: saved generation prompts.
- Cards are 150×210; card IDs match runtime filenames without extensions.
  Card generation prefers per-card artwork, falling back to tier/color artwork.
- Nobles are 150×150. Follow `prompts/noble_prompts.txt`; keep source portraits
  free of overlays. `tools/generate_nobles.py` adds points and requirement squares.
- Single tokens are 60×60. Piles retain approximately 60 px per token,
  not per image. Source-token diameters are in `artwork/gems.txt` and
  `artwork/golds.txt`.
- Conversion/generation commands are documented in `README.md` and tool
  `--help`. They overwrite matching outputs: use temporary directories for
  smoke checks and regenerate only requested assets.

## Working conventions

- Keep changes focused and preserve unrelated user edits.
- Prefer straightforward functions and loops over extra wrappers or defensive
  guards around established invariants.
- Keep arguments required when callers supply them. Add defaults only for
  meaningful optional behavior. Pass interaction state such as `enabled`
  explicitly; initialize empty UI placeholders as disabled.
- Run relevant tests for logic changes. For UI changes, also check Tk
  construction, callbacks, and affected layout where possible.
- Prefer behavioral tests over checks that duplicate definitions or constants.
- Comment obscure library calls and options.
