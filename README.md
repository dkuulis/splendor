# Splendour

A two-player Splendour desktop UI using Tkinter and themed `ttk` widgets.

The app starts with shuffled decks and empty player inventories. The Computer
dropdown switches between Manual (the default) and Pass-only AI. Pass switches turns; two consecutive passes end
the game using score and card-count tie-breaks. The log records actual actions.
Select one to three different gems and use Take selected gems to collect them.
The 10-gem inventory limit is enforced. Buy card is enabled for affordable
market cards, applying owned-card discounts and returning payment to the bank.
Purchases update scores, replace market cards, and trigger the final round at
15 points. Manual lets you control both players. Pass-only AI automatically
passes on the computer's turn. You can switch modes at any time; switching to
Manual cancels a pending AI action. New game preserves the selected mode.

## Adding AI strategies

Add a strategy class under `ai/` with `play_turn(state)`, performing exactly
one legal action through the state's methods, then register its display name
and class in `ai/__init__.py`. The dropdown uses this registry automatically.
Strategies should run quickly because they execute on the UI thread; a future
search-based AI will need background execution.

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
