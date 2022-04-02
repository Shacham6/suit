import importlib
import importlib.readers
import importlib.util
import itertools
import pathlib
import subprocess
from dataclasses import dataclass
from importlib.machinery import SourceFileLoader
from typing import Any, Mapping, MutableMapping

import rich.repr
from box import Box
from rich import print

import suit


def collect():
    """Collect the various suitfiles in the workspace."""
    cwd = pathlib.Path.cwd()
    groups = {}
    tree = {}
    for suit_file in itertools.chain(
            cwd.glob("**/suit"),
            cwd.glob("**/*.suit"),
            cwd.glob("**/suit.py"),
            cwd.glob("**/*.suit.py"),
    ):
        if not suit_file.is_file():
            continue
        if _is_git_ignored(suit_file):
            continue

        if suit_file.name in ("suit", "suit.py"):
            group_name = suit_file.parent.name
        else:
            group_name, *_ = suit_file.name.split(".", maxsplit=1)

        groups[suit_file.parent] = group_name

        tree_path = suit_file.relative_to(cwd).parent
        node = tree
        for path_part in tree_path.parts:
            node = node.setdefault(path_part, {})

        node["__registered__"] = True
        module = SourceFileLoader(str(suit_file), str(suit_file)).load_module()
        for name, value in module.__dict__.items():
            if not isinstance(value, suit.SuitTarget):
                continue
            node[value.name] = {"__is_runnable__": True, "__filepath__": suit_file, "__value__": value}
    return list(collect_tree(tree))


def _is_git_ignored(suit_file: pathlib.Path) -> bool:
    return subprocess.call(["git", "check-ignore", str(suit_file)],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL) == 0


def collect_tree(value, tree_parts=None):
    if not tree_parts:
        tree_parts = []

    if isinstance(value, Mapping):
        for k, v in value.items():
            if k.startswith("__"):
                continue
            if isinstance(v, Mapping):
                if v.get("__is_runnable__", False):
                    yield Box(fullname=":".join([*tree_parts, k]),
                              name=k,
                              filepath=v["__filepath__"],
                              value=v["__value__"])
                elif v.get("__registered__", False):
                    yield from collect_tree(v, tree_parts + [k])
