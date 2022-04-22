import click

from . import _list_targets


@click.group("suit")
def cli():
    pass


cli.add_command(_list_targets.cli_list_targets)

if __name__ == "__main__":
    cli()
