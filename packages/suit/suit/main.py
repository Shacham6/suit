import fnmatch
import itertools
import pathlib
import re
from typing import Tuple

import click
import rich.box
from rich.live import Live
from rich.rule import Rule
from rich.status import Status
from rich.table import Table
from rich.text import Text
from suit.collector import collect

from suit import Runtime, Scope


@click.command("suit")
@click.argument("rules", nargs=-1, type=str)
def cli(rules: Tuple[str, ...]):
    targets = list(collect())
    runtime = Runtime()
    failures = []
    for target in __filter_target_rules(rules, targets):
        group_log_text = Text.assemble(
            "[",
            Text.assemble((":", "dim"),
                          style="italic").join(Text.assemble((l, "yellow")) for l in target.fullname.split(":")), "]")
        runtime.print(Rule(
            Text.assemble(
                Text("Invoking "),
                group_log_text,
            ),
            align="left",
        ))
        try:
            # with runtime.console.status(Text.assemble("Running ", "[", group_log_text, "]"), spinner="aesthetic"):
            target.value.invoke(runtime, Scope(target.fullname, target.filepath.parent, pathlib.Path.cwd()))
        except Exception as e:
            runtime.print(Text.assemble(("FAILURE", "b red"), " ", group_log_text))
            runtime.error(e)
            failures.append((target, failures))

        errors_table = Table(show_header=False, box=rich.box.SIMPLE, show_lines=True)
        for target_failure, e in failures:
            pass


def __filter_target_rules(rules, targets):
    for rule in rules:
        compiled_rule = re.compile(rule)
        for target in targets:
            if compiled_rule.search(target.fullname):
                yield target
