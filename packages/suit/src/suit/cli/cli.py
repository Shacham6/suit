import click

from . import _targets, _scripts


@click.group("suit")
def cli():
    pass


cli.add_command(_targets.cli_targets)
cli.add_command(_scripts.cli_scripts)
cli.add_command(_scripts.cli_run_scripts)

if __name__ == "__main__":
    cli()
