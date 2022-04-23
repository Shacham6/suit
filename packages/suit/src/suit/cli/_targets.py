import click
import click_default_group
import rich.table
from rich.table import Column, Table
from suit.collector import SuitCollector
from suit.console import console


@click.group(
    "targets",
    cls=click_default_group.DefaultGroup,
    default="list",
    default_if_no_args=True,
)
def cli_targets():
    pass


@cli_targets.command("list")
@click.option("--raw", "raw_print", is_flag=True, type=bool)
def cli_list_targets(raw_print: bool):
    suit = SuitCollector.find_root().collect()

    if raw_print:
        for target_name in suit.targets:
            console.print(target_name)
        return

    table = Table(
        Column("Target", style="magenta"),
        show_edge=True,
        box=rich.table.box.SIMPLE,
    )
    for target_name in suit.targets:
        table.add_row(target_name)
    console.print(table)
