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

from suit import Runtime, Scope
from suit.collector import collect


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
        try:
            with runtime._set_message_group(group_log_text):
                target.value.invoke(runtime, Scope(target.fullname, target.filepath.parent, pathlib.Path.cwd()))
        except Exception as e:
            runtime.print(Text.assemble(("FAILURE", "b red"), " ", group_log_text))
            runtime.error(e)
            failures.append((group_log_text, e))

        errors_table = Table(
            "Group", "Failure",
            show_header=True,
            box=rich.box.ROUNDED,
            show_lines=False,
            show_edge=True,
            show_footer=False,
            title="[b red]Failures[/]",
        )
        for target_failure, e in failures:
            errors_table.add_row(target_failure, str(e))
        runtime.console.print(errors_table)


def __filter_target_rules(rules, targets):
    for rule in rules:
        compiled_rule = re.compile(rule)
        for target in targets:
            if compiled_rule.search(target.fullname):
                yield target
