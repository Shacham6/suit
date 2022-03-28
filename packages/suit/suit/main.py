import contextlib
import pathlib
import re
from typing import Tuple

import click
import logbook
from rich.text import Text

from suit.collector import collect

from .runtime import Runtime
from .scope import Scope


@click.command("suit")
@click.argument("rules", nargs=-1, type=str)
def cli(rules: Tuple[str, ...]):
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
            except Exception as e:
                runtime.exception(e)
                failures.append((target, e))


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
