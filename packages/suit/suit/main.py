import contextlib
import pathlib
import re
from typing import Iterable, List, Optional, Tuple

import click
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


@click.command("suit")
@click.argument("rules", nargs=-1, type=str)
@click.option("--config",
              "-c",
              "config",
              type=click.Path(exists=True, readable=True, path_type=pathlib.Path),
              callback=__get_configuration)
def cli(rules: Tuple[str, ...], config: Box):
    targets = list(collect())
    failures = []
    for target in __filter_target_rules(rules, targets):
        target_scope = Scope(target.fullname, target.filepath.parent, pathlib.Path.cwd())
        runtime = Runtime(target_scope)

        group_log_text = Text.assemble(
            Text.assemble((":", "dim"),
                          style="italic").join(Text.assemble((l, "yellow")) for l in target.fullname.split(":")),)
        with _push_extras(scope=group_log_text):
            try:
                target.value.invoke(runtime, target_scope)
            except Exception as exc:
                runtime.exception(exc)
                failures.append((target, exc))


@contextlib.contextmanager
def _push_extras(**extras):

    def _tmp(record: logbook.LogRecord):
        nonlocal extras
        for k, v in extras.items():
            record.extra[k] = v

    with logbook.Processor(_tmp) as a:
        yield a


def __filter_target_rules(rules, targets):
    for rule in rules:
        compiled_rule = re.compile(rule)
        for target in targets:
            if compiled_rule.search(target.fullname):
                yield target
