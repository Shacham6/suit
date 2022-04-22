import click

from . import _targets


@click.group("suit")
def cli():
    pass


cli.add_command(_targets.cli_targets)

if __name__ == "__main__":
    cli()
