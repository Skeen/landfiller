import os
import platform
import sys
from pathlib import Path
from textwrap import dedent
from typing import Annotated
from typing import Optional

import draftsman.data.tiles
import pyperclip
import typer
from draftsman.blueprintable import Blueprint
from draftsman.env import update
from draftsman.tile import Tile
from rich import print
from rich.progress import Progress
from rich.progress import SpinnerColumn
from rich.progress import TextColumn
from rich.progress import track


def envvar(varname: str) -> dict[str, str | bool]:
    return {"envvar": f"LANDFILLER_{varname.upper()}", "show_envvar": False}


def modpath() -> Path | None:
    match platform.system():
        case "Windows":
            return Path(os.path.expandvars("%AppData%\\Factorio\\Mods\\"))
        case "Linux":
            return Path("~/.factorio/mods/").expanduser()
        case "Darwin":
            return Path("~/Library/Application Support/factorio/mods/").expanduser()
        case _:
            return None


app = typer.Typer(rich_markup_mode="rich")


@app.command(
    help=dedent(
        """
        Add landfill under a factorio blueprint.

        Defaults to consuming from stdin and outputting to stdout.
        """
    ),
    epilog="[italic]Note: All arguments can be given by environmental variable using the [green]`LANDFILLER_`[/green] prefix.[/italic]",
)
def main(
    input: Annotated[
        typer.FileText,
        typer.Option(
            help="The blueprint to add landfill to.",
            show_default=False,
            rich_help_panel="IO Control",
            **envvar("blueprint"),
        ),
    ] = sys.stdin,
    output: Annotated[
        typer.FileTextWrite,
        typer.Option(
            help="Where to output the modified blueprint.",
            show_default=False,
            rich_help_panel="IO Control",
            **envvar("output"),
        ),
    ] = sys.stdout,
    clipboard_input: Annotated[
        bool,
        typer.Option(
            "--clip-in",
            help="Consume the input blueprint from the clipboard.",
            rich_help_panel="IO Control",
            **envvar("clip-in"),
        ),
    ] = False,
    clipboard_output: Annotated[
        bool,
        typer.Option(
            "--clip-out",
            help="Output the modified blueprint to the clipboard.",
            rich_help_panel="IO Control",
            **envvar("clip-out"),
        ),
    ] = False,
    modpath: Annotated[
        Optional[Path],
        typer.Option(
            help="Path to the factorio mods folder.",
            rich_help_panel="Configuration",
            exists=True,
            file_okay=False,
            dir_okay=True,
            writable=False,
            readable=True,
            resolve_path=True,
            **envvar("modpath"),
        ),
    ] = modpath(),
    ignore_mods: Annotated[
        bool,
        typer.Option(
            "--ignore-mods",
            help="Ignore mods even if detected.",
            rich_help_panel="Configuration",
            **envvar("ignore-mods"),
        ),
    ] = False,
    landfill: Annotated[
        str,
        typer.Option(
            help="The kind of landfill to add.",
            rich_help_panel="Configuration",
            **envvar("landfill"),
        ),
    ] = "landfill",
    strip: Annotated[
        bool,
        typer.Option(
            "--strip",
            help="Forcefully strip existing landfill.",
            rich_help_panel="Existing tile management",
            show_default=False,
            **envvar("strip"),
        ),
    ] = False,
    merge: Annotated[
        bool,
        typer.Option(
            "--merge",
            help="Merge new landfill with existing landfill.",
            rich_help_panel="Existing tile management",
            show_default=False,
            **envvar("merge"),
        ),
    ] = False,
) -> None:
    if strip and merge:
        print(
            "[bold red]Error:[/bold red] Cannot provide [green]`--strip`[/green] and [green]`--merge`[/green] at the same time."
        )
        raise typer.Exit(code=1)

    if clipboard_input:
        blueprint_string = pyperclip.paste()
    else:
        blueprint_string = input.read()

    if modpath and not ignore_mods:
        with Progress(SpinnerColumn(), TextColumn("{task.description}")) as progress:
            progress.add_task(description="Loading Mods...", total=None)
            update(verbose=False, path=str(modpath))

    tiles = draftsman.data.tiles.raw.keys()
    if landfill not in tiles:
        raise typer.BadParameter(
            "Bad landfill parameter, must be one of: " + ", ".join(tiles)
        )

    blueprint = Blueprint(blueprint_string)

    if blueprint.tiles and not (strip or merge):
        num_tiles = len(blueprint.tiles)
        print(f"[bold red]Would override {num_tiles} tiles![/bold red]")
        print("If you intended to do this please provide [green]`--strip`[/green]")
        print("If you intended to merge use [green]`--merge`[/green] instead")
        raise typer.Exit(code=1)

    if strip:
        blueprint.tiles.clear()

    # Seed existing tiles so we do not create overlapping ones
    filled_tiles = set()
    for tile in blueprint.tiles:
        filled_tiles.add((tile.position.x, tile.position.y))

    def generate_tiles(entity):
        ecolset = entity.get_world_collision_set()
        bb = ecolset.get_bounding_box()

        start_x = round(bb.world_top_left[0]) - 2
        end_x = round(bb.world_bot_right[0]) + 2

        start_y = round(bb.world_top_left[1]) - 2
        end_y = round(bb.world_bot_right[1]) + 2

        for tx in range(start_x, end_x):
            for ty in range(start_y, end_y):
                if (tx, ty) in filled_tiles:
                    continue

                t = Tile(landfill, (tx, ty))
                tcolset = t.get_world_collision_set()
                if tcolset.overlaps(ecolset):
                    filled_tiles.add((tx, ty))
                    yield t

    new_landfill = [
        tile
        for entity in track(blueprint.entities, description="Generating fill...")
        for tile in generate_tiles(entity)
    ]

    for tile in track(new_landfill, description="Adding landfill..."):
        blueprint.tiles.append(tile)

    with Progress(SpinnerColumn(), TextColumn("{task.description}")) as progress:
        progress.add_task(description="Generating blueprint", total=None)
        output_blueprint = blueprint.to_string()

    if clipboard_output:
        pyperclip.copy(output_blueprint)
    else:
        output.write(output_blueprint)


if __name__ == "__main__":
    app()
