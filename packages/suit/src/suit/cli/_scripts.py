import click


@click.group("scripts")
def cli_scripts():
    pass


@cli_scripts.command("list")
def cli_list_scripts():
    pass
