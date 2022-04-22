import itertools
import pathlib
from typing import Any, Iterable, List, Mapping, NamedTuple

import tomli


class SuitCollector:
    """
    Collect the entire array of suit configurations.
    """

    def __init__(self, root: pathlib.Path):
        self.__root = root

    def collect(self):
        """Collect all targets in the directory structure"""
        for found_project_file in self.__root.glob("**/pyproject.toml"):
            with found_project_file.open("rb") as found_project_file_io:
                project_data = tomli.load(found_project_file_io)
                if not _pyproject_uses_suit(project_data):
                    continue
                yield Target(
                    root=self.__root,
                    target_path=found_project_file,
                    target_data=project_data["tool"]["suit"],
                )


class Target(NamedTuple):
    """
    A suit-using target.
    """

    root: pathlib.Path
    target_data: Mapping[str, Any]
    target_path: pathlib.Path


def _pyproject_uses_suit(pyproject_data: Mapping[str, Any]) -> bool:
    if "suit" not in pyproject_data.get("tool", {}):
        return False
    return True


def _find_root_directory(cwd: pathlib.Path = pathlib.Path.cwd()) -> pathlib.Path:
    if cwd.is_file():
        cwd = cwd.parent
    searched_paths = [cwd, *cwd.parents]
    for loc in searched_paths:
        if loc.joinpath("suit.toml").exists():
            return loc
    raise RootDirectoryNotFound(searched_paths=searched_paths)


class RootDirectoryNotFound(Exception):
    def __init__(self, searched_paths: List[pathlib.Path]):
        super().__init__(
            f"Could not find `suit.toml` file, that signifies root directory. Searched: {searched_paths}"
        )
        self.searched_paths = searched_paths
