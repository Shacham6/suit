import importlib
import importlib.util
import itertools
import pathlib

import click
import rich.repr

import suit


@click.command("suit")
def cli():
    cwd = pathlib.Path.cwd()
    targets = []
    for suit_file in itertools.chain(
            cwd.glob("**/suit"),
            cwd.glob("**/*.suit"),
            cwd.glob("**/suit.py"),
            cwd.glob("**/*.suit.py"),
    ):
        if not suit_file.is_file():
            continue
        res = importlib.util.spec_from_file_location("something", str(suit_file))
        module = res.loader.load_module("something")
        for name, value in module.__dict__.items():
            if not isinstance(value, suit._SuitTarget):
                continue
            targets.append(_Target(f"targets", name, suit_file, value.fn))
        print(suit_file)
    print(targets)


@rich.repr.auto()
class _Target:

    def __init__(self, target_group: str, target_name: str, defining_path: pathlib.Path, fn):
        self.__target_group = target_group
        self.__target_name = target_name
        self.__defining_path = defining_path
        self.__fn = fn

    @property
    def target_group(self):
        return self.__target_group

    @property
    def target_name(self):
        return self.__target_name

    @property
    def path(self):
        return self.__defining_path

    def __rich_repr__(self):
        yield "group", self.target_group
        yield "name", self.target_name


cli()
