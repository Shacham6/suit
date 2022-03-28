import fnmatch
import itertools
import pathlib
import re
from typing import Tuple

import click
from rich.rule import Rule
from rich.text import Text
from suit_core.collector import collect

from suit import Runtime, Scope


@click.command("suit")
@click.argument("rules", nargs=-1, type=str)
def cli(rules: Tuple[str, ...]):
    targets = list(collect())
    runtime = Runtime()
    for target in __filter_target_rules(rules, targets):
        runtime.log(
            Rule(
                Text.assemble(
                    Text("Invoking ["),
                    Text(":", style="italic").join(Text.assemble((l, "bold")) for l in target.fullname.split(":")),
                    Text("]"),
                ),
                align="center",
            ))
        try:
            target.value.invoke(runtime, Scope(target.filepath.parent, pathlib.Path.cwd()))
        except Exception as e:
            runtime.log(ej)


def __filter_target_rules(rules, targets):
    for rule in rules:
        compiled_rule = re.compile(rule)
        for target in targets:
            if compiled_rule.search(target.fullname):
                yield target
