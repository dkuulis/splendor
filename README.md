# Splendour

A two-player Splendour desktop UI using Tkinter and themed `ttk` widgets.

Currently a layout prototype with sample player balances, a three-level card
market, and a gem bank. Gem selection updates the selection summary; gameplay
buttons are disabled until rules and the computer opponent are implemented.

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
