import click

from suit.collector import SuitCollector
from suit.console import console
from rich.table import Table, Column


@click.group("targets")
def cli_targets():
    pass


@cli_targets.command("list")
@click.option("--raw", "raw_print", is_flag=True, type=bool)
def cli_list_targets(raw_print: bool):
    suit = SuitCollector.find_root().collect()

    if raw_print:
        for _, target in suit.targets.items():
            console.print(target.name)
        return

    table = Table(Column("Target", justify="center"), show_edge=False)
    for _, target in suit.targets.items():
        table.add_row(target.name)
    console.print(table)
