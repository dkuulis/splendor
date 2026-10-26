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
  `selection.py` owns pending choices and boolean permissions for selection
  interactions and action confirmation, and dispatches the selected action.
  `state.py` owns card affordability, action execution, and market replacement.
  State actions take explicit arguments: `buy_card(card)`, `reserve_card(card)`,
  and `take_tokens(tokens)`; Selection dispatch supplies its pending choices.
  Action methods and Selection dispatch execute without validation. Callers must
  choose an allowed action; the UI uses Selection permissions to enable controls.
- `player.py` owns holdings and derived points, discounts, capacity, and payment.
  Use these calculations through the relevant player.
- `State.finish_turn(passed)` updates consecutive passes, awards a noble,
  and advances the turn. Actions pass `passed` explicitly. Selection dispatch
  clears pending choices after execution; State does not own selection.
  `noble.py` handles awards; `turn.py` handles final rounds, completion, and ties.
  `initialize.py` defines cards, nobles, and shuffled setup.
- `ai/` strategies implement `make_selection(state, selection)` and prepare
  one legal selection without mutating State or executing an action.
  App displays the selection, then dispatches the action in a delayed callback.
  Register them in `ai/__init__.py`.
- `app/app.py` owns separate `state` and `selection` models, assembles panels,
  delegates action dispatch to Selection, and schedules AI callbacks.
  `selection_panel` is the widget; Restart replaces both models.
  AI runs on the UI thread: keep strategies quick and cancel pending callbacks
  on Restart and window destruction.
- `app/selection_panel.py` contains one action button and a separate Restart.
  The action button follows `Selection.action_kind`: Buy, Reserve, Take,
  or Pass. Pass ends the turn without collecting.
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
- Use `TOKENS` for display and selection ordering. Payment calculations
  can iterate over cost entries directly.
- `State.supply` holds available tokens; `Player.tokens` holds owned tokens.
  Selection is pending and does not transfer tokens. Dispatching an action
  clears it.
  `Selection.action_kind` derives pass, buy, reserve, or take from pending
  choices. Empty selection means pass. Market-card selection clears selected
  tokens, then adds gold for reservation only if the card is unaffordable.
  Gold can be selected manually only with an affordable market card and cannot
  be deselected while that card is unaffordable. Unaffordable reserved cards
  cannot be selected. Selection owns these decisions; the UI delegates clicks.
- Missing entries in sparse token/cost/selection dictionaries mean zero.
  Gem keys in `Player.cards` and `Player.discounts`, and tiers 1–3 in
  `State.market` and `State.decks`, are always present; index them directly.
- Discounts derive only from owned cards. Points include cards and nobles.
  Payments use matching gems before gold and include only nonzero amounts.
- Noble requirements count permanent card bonuses, not tokens. Award at most
  the first qualifying available noble each turn, without spending holdings
  or replacing the noble, before checking turn completion.

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
