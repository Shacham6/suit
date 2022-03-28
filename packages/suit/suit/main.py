import fnmatch
import itertools
import re
from typing import Tuple

import click
from rich.rule import Rule
from rich.text import Text
from suit_core.collector import collect

from suit.runtime import Runtime


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
        target.value.invoke(runtime)


def __filter_target_rules(rules, targets):
    for rule in rules:
        compiled_rule = re.compile(rule)
        for target in targets:
            if compiled_rule.search(target.fullname):
                yield target
