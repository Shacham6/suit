from __future__ import annotations

import pathlib
from typing import Any, List, Mapping, NamedTuple

import tomli


class SuitCollector:
    """
    Collect the entire array of suit configurations.
    """

    def __init__(self, root: pathlib.Path):
        self.__root = root

    def collect(self) -> Suit:
        """Collect all targets in the directory structure"""
        return Suit(
            self.__root,
            targets=list(self.__collect_targets()),
        )

    def __collect_targets(self):
        for found_project_file in self.__root.glob("**/pyproject.toml"):
            with found_project_file.open("rb") as found_project_file_io:
                project_data = tomli.load(found_project_file_io)
                if not _pyproject_uses_suit(project_data):
                    continue
                yield Target(
                    path=found_project_file,
                    data=project_data["tool"]["suit"],
                )


class Target(NamedTuple):
    """
    A project target.
    """

    path: pathlib.Path
    data: Mapping[str, Any]


class Suit(NamedTuple):
    """
    The general suit configurations.
    """

    root: pathlib.Path
    targets: List[Target]


def _pyproject_uses_suit(pyproject_data: Mapping[str, Any]) -> bool:
    if "suit" not in pyproject_data.get("tool", {}):
        return False
    return True


def _find_root_configuration(cwd: pathlib.Path = pathlib.Path.cwd()) -> pathlib.Path:
    if cwd.is_file():
        cwd = cwd.parent
    searched_paths = [cwd, *cwd.parents]
    for loc in searched_paths:
        suit_file = loc.joinpath("suit.toml")
        if suit_file.exists():
            return suit_file
    raise RootDirectoryNotFound(searched_paths=searched_paths)


class RootDirectoryNotFound(Exception):
    def __init__(self, searched_paths: List[pathlib.Path]):
        super().__init__(
            f"Could not find `suit.toml` file, that signifies root directory. Searched: {searched_paths}"
        )
        self.searched_paths = searched_paths
