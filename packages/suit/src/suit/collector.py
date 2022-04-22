from __future__ import annotations

import functools
import pathlib
import weakref
from typing import Any, Iterator, List, Mapping, NamedTuple, Optional

import tomli


def _pyproject_uses_suit(pyproject_data: Mapping[str, Any]) -> bool:
    return "suit" in pyproject_data.get("tool", {})


def _find_root_configuration(cwd: Optional[pathlib.Path] = None) -> pathlib.Path:
    if not cwd:
        cwd = pathlib.Path.cwd()

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


class SuitCollector:
    """
    Collect the entire array of suit configurations.
    """

    def __init__(self, root: pathlib.Path, local_configurations: Mapping[str, Any]):
        self.__root = root
        self.__local_config = local_configurations

    @classmethod
    def find_root(cls, starting_search_location: Optional[pathlib.Path] = None):
        """
        Search and initialize the collector at the root of the project.
        """
        if not starting_search_location:
            starting_search_location = pathlib.Path.cwd()
        local_config_file = _find_root_configuration(starting_search_location)
        with local_config_file.open("rb") as local_config_io:
            local_configurations = tomli.load(local_config_io)
        return cls(
            root=local_config_file.parent,
            local_configurations=local_configurations["suit"],
        )

    def collect(self) -> Suit:
        """Collect all targets in the directory structure"""
        return Suit(
            self.__root,
            local_config=self.__local_config,
            raw_targets=list(self.__collect_targets()),
        )

    def __collect_targets(self):
        for found_project_file in self.__root.glob("**/pyproject.toml"):
            with found_project_file.open("rb") as found_project_file_io:
                project_data = tomli.load(found_project_file_io)
                if not _pyproject_uses_suit(project_data):
                    continue
                yield _TargetConfig(
                    path=found_project_file,
                    data=project_data["tool"]["suit"],
                )


class _TargetConfig(NamedTuple):
    """
    A project target.
    """

    path: pathlib.Path
    data: Mapping[str, Any]


class Suit:
    """
    The general suit configurations.
    """

    def __init__(
        self,
        root: pathlib.Path,
        local_config: Mapping[str, Any],
        raw_targets: List[_TargetConfig],
    ):
        self.root = root
        self.local_config = local_config
        self.raw_targets = raw_targets
        self.targets = Targets(weakref.ref(self))


class Target:
    def __init__(self):
        pass


class Targets(Mapping[str, Target]):
    def __init__(
        self,
        suit_ref: weakref.ReferenceType[Suit],
    ):
        self.__suit_ref = suit_ref
        self.__canonized = {
            str(raw_target.path.relative_to(self.__suit_ref().root)): raw_target
            for raw_target in self.__suit_ref().raw_targets
        }

    def __getitem__(self, __k: str) -> Target:
        return Target()

    def __iter__(self) -> Iterator[str]:
        return iter(self.__canonized)

    def __len__(self) -> int:
        return len(self.__canonized)
