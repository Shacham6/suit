import contextlib
import pathlib
import re
from typing import Iterable, List, Optional, Tuple

import click
import click_default_group
import logbook
from box import Box
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
        return Box.from_toml(filename=value)

    if found_target := __search_root_file("suit.toml"):
        return Box.from_toml(filename=found_target)

    return Box()


def __search_root_file(filename) -> Optional[pathlib.Path]:
    for search_location in __walk_backwards(pathlib.Path.cwd()):
        target = search_location.joinpath(filename)
        if target.exists():
            return target
    return


def __walk_backwards(location: pathlib.Path) -> Iterable[pathlib.Path]:
    """ Walk from location up to the root path of the system. """
    if location.is_file():
        location = location.parent
    yield location
    yield from location.parents


pass_config = click.option(
    "--config",
    "-c",
    "config",
    type=click.Path(exists=True, readable=True, path_type=pathlib.Path),
    callback=__get_configuration,
)


@click.group("suit")
@pass_config
@click.pass_context
def cli(ctx: click.Context, config: Box):
    # pylint: disable=missing-function-docstring
    ctx.ensure_object(Box)
    ctx.obj.config = config


@cli.command("run")
@click.argument("rules", nargs=-1, type=str)
def run_cli(rules: Tuple[str, ...]):
    # pylint: disable=missing-function-docstring
    targets = list(collect())
    executor = TargetsExecutor(list(__filter_target_rules(rules, targets)))
    executor.execute_sequentally()


class TargetsExecutor:

    def __init__(self, targets):
        self.__targets = targets

    def execute_sequentally(self):
        failures = []
        for target in self.__targets:
            target_scope = Scope(target.fullname, target.filepath.parent, pathlib.Path.cwd())
            runtime = Runtime(target_scope)

            group_log_text = Text.assemble(
                Text.assemble((":", "dim"), style="italic").join(
                    Text.assemble((target_part_name, "yellow")) for target_part_name in target.fullname.split(":")),)
            with _push_extras(scope=group_log_text):
                try:
                    target.value.invoke(runtime, target_scope)
                except Exception as exc:  # pylint: disable=broad-except
                    runtime.exception(exc)
                    failures.append((target, exc))


@contextlib.contextmanager
def _push_extras(**extras):

    def _tmp(record: logbook.LogRecord):
        nonlocal extras
        for key, value in extras.items():
            record.extra[key] = value

    with logbook.Processor(_tmp) as thing:
        yield thing


def __filter_target_rules(rules, targets):
    for rule in rules:
        compiled_rule = re.compile(rule)
        for target in targets:
            if compiled_rule.search(target.fullname):
                yield target
