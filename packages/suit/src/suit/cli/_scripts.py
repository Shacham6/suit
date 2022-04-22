import json

import click
import click_default_group
import rich.table
from rich.console import Group
from rich.padding import Padding
from rich.table import Column, Table
from suit.collector import SuitCollector
from suit.console import console


@click.group(
    "scripts",
    cls=click_default_group.DefaultGroup,
    default="list",
    default_if_no_args=True,
)
def cli_scripts():
    pass


@cli_scripts.command("list")
@click.option("--json", "should_print_json", type=bool, is_flag=True)
def cli_list_scripts(should_print_json: bool = False):
    suit = SuitCollector.find_root().collect()
    scripts = {}

    for target_name, target in suit.targets.items():
        for script_name in target.scripts:
            scripts.setdefault(script_name, []).append(target_name)

    if should_print_json:
        print(json.dumps(scripts, indent=2))
        return

    table = Table(
        Column("Scripts", justify="center", style="magenta"),
        Column("Targets", justify="center", style="italic"),
        show_edge=True,
        box=rich.table.box.SIMPLE,
    )

    for script_name, targets in scripts.items():
        table.add_row(script_name, Padding(Group(*targets), (0, 0, 1, 0)))
    console.print(table)
