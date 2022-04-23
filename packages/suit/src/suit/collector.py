from __future__ import annotations

import pathlib
from typing import Any, List, Mapping, Optional

import tomli

from .targets import TargetConfig
from .suit_config import SuitConfig


def _pyproject_uses_suit(pyproject_data: Mapping[str, Any]) -> bool:
    return "target" in pyproject_data.get("tool", {}).get("suit", {})


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
        super().__init__(f"Could not find `suit.toml` file, that signifies root directory. Searched: {searched_paths}")
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

    def collect(self) -> SuitConfig:
        """Collect all targets in the directory structure"""
        return SuitConfig(
            self.__root,
            project_config=self.__local_config,
            targets=list(self.__collect_targets()),
        )

    def __collect_targets(self):
        for found_project_file in self.__root.glob("**/pyproject.toml"):
            with found_project_file.open("rb") as found_project_file_io:
                project_data = tomli.load(found_project_file_io)
                if not _pyproject_uses_suit(project_data):
                    continue
                yield TargetConfig.from_mapping(
                    path=found_project_file.parent,
                    data=project_data["tool"]["suit"]["target"],
                )
