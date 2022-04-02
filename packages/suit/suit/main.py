import contextlib
import functools
import pathlib
import re
import sys
from typing import Iterable, Optional, Tuple

import click
import logbook
import rich.box
from box import Box
from rich import print
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

from suit.collector import collect

from .runtime import Runtime
from .scope import Scope


def __get_configuration(
    ctx: click.Context,
    param: click.Parameter,
    value: Optional[pathlib.Path],
) -> Box:
    # pylint: disable=unused-argument
    if value:
        return Box(Box.from_toml(filename=value), _root=value.parent)

    if found_target := __search_root_file("suit.toml"):
        return Box(Box.from_toml(filename=found_target), _root=found_target.parent)

    return Box(_root=pathlib.Path.cwd())


def __search_root_file(filename) -> Optional[pathlib.Path]:
    for search_location in __walk_backwards(pathlib.Path.cwd()):
        target = search_location.joinpath(filename)
        if target.exists():
            return target
    return


def __walk_backwards(location: pathlib.Path) -> Iterable[pathlib.Path]:
    """Walk from location up to the root path of the system."""
    if location.is_file():
        location = location.parent
    yield location
    yield from location.parents


@click.group("suit")
@click.option(
    "--config",
    "-c",
    "config",
    type=click.Path(exists=True, readable=True, path_type=pathlib.Path),
    callback=__get_configuration,
)
@click.pass_context
def cli(ctx: click.Context, config: Box):
    # pylint: disable=missing-function-docstring
    ctx.ensure_object(Box)
    ctx.obj.config = config
    extra_imports = config["suit"].get("imports", [])

    if isinstance(extra_imports, str):
        extra_imports = [extra_imports]

    for import_location in extra_imports:
        sys.path.append(import_location)


class pass_config:
    def __init__(self, name):
        self.__name = name

    def __call__(self, func):
        @click.pass_context
        def _tmp(ctx: click.Context, *args, **kwargs):
            return ctx.invoke(func, *args, **{**kwargs, self.__name: ctx.obj.config})

        return functools.update_wrapper(_tmp, func)


@cli.command("list")
@click.argument("rules", nargs=-1, type=str)
@pass_config("config")
def list_cli(rules: Tuple[str, ...], config: Box):
    targets = list(collect(config._root))
    if rules:
        targets = list(__filter_target_rules(rules, targets))
    print(_build_targets_view(targets))


def _build_targets_view(targets):
    table = Table("Target", "Path", box=rich.box.SIMPLE_HEAD)
    for target in targets:
        table.add_row(
            _build_target_name_view(target.fullname),
            _build_path_view(target.filepath),
        )
    return table


def _build_path_view(path: pathlib.Path):
    return Text(str(path), "cyan")


@cli.command("info")
@pass_config("config")
def info_cli(config: Box):
    info_table = Table("Key", "Value", box=rich.box.SIMPLE_HEAD)
    info_table.add_row("_root_dir", _build_path_view(config._root))

    targets = list(collect(config._root))
    info_table.add_row("len(targets)", Text(str(len(targets))))
    print(info_table)


@cli.command("run")
@click.argument("rules", nargs=-1, type=str)
@pass_config("config")
def run_cli(rules: Tuple[str, ...], config: Box):
    # pylint: disable=missing-function-docstring
    targets = list(collect(config._root))
    executor = TargetsExecutor(list(__filter_target_rules(rules, targets)), config)
    failures = executor.execute_sequentally()
    exit(1 if failures else 0)


class TargetsExecutor:
    def __init__(self, targets, config: Box):
        self.__targets = targets
        self.__config = config

    def execute_sequentally(self):
        failures = []
        for target in self.__targets:
            target_scope = Scope(
                target.fullname, target.filepath.parent, pathlib.Path.cwd()
            )
            runtime = Runtime(target_scope, Box(self.__config, frozen_box=True))

            group_log_text = Text.assemble(_build_target_name_view(target.fullname))
            runtime.info(Rule(Text.assemble("Executing target ", group_log_text)))
            with _push_extras(scope=group_log_text):
                try:
                    target.value.invoke(runtime, target_scope)
                except Exception as exc:  # pylint: disable=broad-except
                    runtime.exception(exc)
                    failures.append((target, exc))
        return failures


@contextlib.contextmanager
def _push_extras(**extras):
    def _tmp(record: logbook.LogRecord):
        nonlocal extras
        for key, value in extras.items():
            record.extra[key] = value

    with logbook.Processor(_tmp) as thing:
        yield thing


def __filter_target_rules(rules, targets):
    found_targets = set()
    for rule in rules:
        compiled_rule = re.compile(rule)
        for target in targets:
            if not compiled_rule.search(target.fullname):
                continue
            if target.fullname not in found_targets:
                found_targets.add(target.fullname)
                yield target


def _build_target_name_view(target_name):
    return Text.assemble((":", "dim"), style="italic").join(
        Text.assemble((target_part_name, "yellow"))
        for target_part_name in target_name.split(":")
    )
