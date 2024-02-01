# landfiller

![A logo generated with 'factorio-draftsman/draftsman_logo.py'](https://github.com/Skeen/landfiller/raw/main/docs/img/logo.png)

[![Code style: black](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

A little tool for adding landfill to blueprints from the game [Factorio](https://factorio.com/).

| before   | landfill | after    |
|----------|----------|----------|
| ![before](https://github.com/Skeen/landfiller/raw/main/docs/img/before.png) | ![before](https://github.com/Skeen/landfiller/raw/main/docs/img/landfill.png) | ![before](https://github.com/Skeen/landfiller/raw/main/docs/img/after.png) |

--------------------------------------------------------------------------------
## Usage

### Installation:
```
poetry install
```
This will install all dependencies.

--------------------------------------------------------------------------------
### How to use landfiller:
```
poetry run python main.py [FLAGS]
```

Assuming a blueprint is already in the clipboard, such as from copying in-game:

![A usage example generated with termtosvg](https://github.com/Skeen/landfiller/raw/main/docs/img/term.svg)

Similarly `--clip-out` can be used to copy the result directly to the clipboard.

### Usage help:
```
> poetry run python main.py --help

 Usage: main.py [OPTIONS]

 Add landfill under a factorio blueprint.
 Defaults to consuming from stdin and outputting to stdout.

╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.      │
│ --show-completion             Show completion for the current shell, to copy │
│                               it or customize the installation.              │
│ --help                        Show this message and exit.                    │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ IO Control ─────────────────────────────────────────────────────────────────╮
│ --input           FILENAME  The blueprint to add landfill to.                │
│ --output          FILENAME  Where to output the modified blueprint.          │
│ --clip-in                   Consume the input blueprint from the clipboard.  │
│ --clip-out                  Output the modified blueprint to the clipboard.  │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Configuration ──────────────────────────────────────────────────────────────╮
│ --modpath            DIRECTORY  Path to the factorio mods folder.            │
│                                 [default: /home/skeen/.factorio/mods]        │
│ --ignore-mods                   Ignore mods even if detected.                │
│ --landfill           TEXT       The kind of landfill to add.                 │
│                                 [default: landfill]                          │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Existing tile management ───────────────────────────────────────────────────╮
│ --strip          Forcefully strip existing landfill.                         │
│ --merge          Merge new landfill with existing landfill.                  │
╰──────────────────────────────────────────────────────────────────────────────╯

 Note: All arguments can be given by environmental variable using the
 `LANDFILLER_` prefix.
```
