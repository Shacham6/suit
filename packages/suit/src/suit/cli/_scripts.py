from __future__ import annotations

import json
import re
import sys
from typing import Iterable, List, Tuple, cast

import click
import click_default_group
import rich.table
from rich.console import Group
from rich.padding import Padding
from rich.table import Column, Table
from rich.text import Text
from suit.cli.executor import ExecutionPlanStage, ScriptFailedError, TargetScriptExecutor
from suit.collector import SuitCollector
from suit.console import console
from suit.scripts.resolver import resolve_scripts


@click.group(
    "scripts",
    cls=click_default_group.DefaultGroup,
    default="list",
    default_if_no_args=True,
)
def cli_scripts():
    pass


def __to_patterns(ctx: click.Context, param: click.Parameter, value: Tuple[str, ...]) -> _Patterns:
    return _Patterns(value)


@cli_scripts.command("list")
@click.option("--json", "should_print_json", type=bool, is_flag=True)
@click.option(
    "-t",
    "--target-pattern",
    "target_patterns",
    type=str,
    multiple=True,
    callback=__to_patterns,
)
def cli_list_scripts(target_patterns: _Patterns, should_print_json: bool = False):
    suit = SuitCollector.find_root().collect()
    scripts = {}

    for target_name, target in suit.targets.items():
        if not target_patterns.match(target_name):
            continue

        for script_name in resolve_scripts(suit, target):
            scripts.setdefault(script_name, []).append(target_name)

    if should_print_json:
        print(json.dumps(scripts, indent=2))
        return

    table = Table(
        Column("Scripts", style="magenta"),
        Column("Targets", style="italic"),
        show_edge=True,
        box=rich.table.box.SIMPLE,
    )

    for script_name, targets in scripts.items():
        table.add_row(script_name, Padding(Group(*targets), (0, 0, 1, 0)))
    console.print(table)


@cli_scripts.command("run")
@click.argument(
    "scripts",
    nargs=-1,
)
@click.option(
    "-t",
    "--target-pattern",
    "target_patterns",
    type=str,
    multiple=True,
    callback=__to_patterns,
)
@click.option("--dry-run", "is_dry_run", is_flag=True, type=bool)
def cli_run_scripts(scripts: Tuple[str, ...], target_patterns: _Patterns, is_dry_run: bool = False):
    if not scripts:
        raise click.UsageError("Must provide scripts to run!")
    suit = SuitCollector.find_root().collect()

    found = []
    for script_name in scripts:
        for target_name, target in suit.targets.items():
            if not target_patterns.match(target_name):
                continue
            for target_script_name, target_script in target.scripts.items():
                if script_name != target_script_name:
                    continue

                # target_script.execute()
                found.append(ExecutionPlanStage(target_name, target_script_name, target_script))
    try:
        TargetScriptExecutor(found).execute(is_dry_run=is_dry_run)
    except ScriptFailedError as script_failed:
        sys.exit(script_failed.return_code)


class _Patterns:
    def __init__(self, patterns: Iterable[str]):
        self.__patterns = [re.compile(pattern) for pattern in patterns]

    def match(self, name: str) -> bool:
        if not self.__patterns:
            return True
        return any(pattern.search(name) for pattern in self.__patterns)
