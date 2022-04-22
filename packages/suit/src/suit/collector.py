from __future__ import annotations

import fnmatch
import functools
import pathlib
import re
import shlex
import weakref
from subprocess import PIPE, Popen
from typing import (
    IO,
    Any,
    AnyStr,
    Iterable,
    Iterator,
    List,
    Mapping,
    NamedTuple,
    Optional,
    cast,
)

import rich.repr
import tomli
from box import Box


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
            project_config=self.__local_config,
            raw_targets=list(self.__collect_targets()),
        )

    def __collect_targets(self):
        for found_project_file in self.__root.glob("**/pyproject.toml"):
            with found_project_file.open("rb") as found_project_file_io:
                project_data = tomli.load(found_project_file_io)
                if not _pyproject_uses_suit(project_data):
                    continue
                yield _TargetConfig(
                    path=found_project_file.parent,
                    data=project_data["tool"]["suit"],
                )


class _TargetConfig(NamedTuple):
    """
    A project target.
    """

    path: pathlib.Path
    data: Mapping[str, Any]


@rich.repr.auto()
class Suit:
    """
    The general suit configurations.
    """

    def __init__(
        self,
        root: pathlib.Path,
        project_config: Mapping[str, Any],
        raw_targets: List[_TargetConfig],
    ):
        self.__root = root
        self.__project_config = project_config
        self.__raw_targets = raw_targets
        self.__targets = Targets(weakref.ref(self))
        self.__templates = project_config.get("templates", {})

    @property
    def root(self) -> pathlib.Path:
        return self.__root

    @property
    def project_config(self) -> Mapping[str, Any]:
        return self.__project_config

    @property
    def raw_targets(self) -> List[_TargetConfig]:
        return self.__raw_targets

    @property
    def targets(self) -> Targets:
        return self.__targets

    @property
    def templates(self) -> Mapping[str, Any]:
        return self.__templates

    def __rich_repr__(self) -> rich.repr.RichReprResult:
        yield "root", self.__root
        yield "project_config", self.__project_config
        yield "raw_targets", self.__raw_targets


class Target:
    def __init__(self, name: str, suit: Suit, raw_target: _TargetConfig):
        self.__name = name
        self.__suit = suit
        self.__raw_target = raw_target

        raw_scripts_config = raw_target.data.get("target", {}).get("scripts", {})

        scripts = {}
        for script_name, value in raw_scripts_config.items():
            scripts[script_name] = TargetScript.compile_inline(
                value, self.__suit, self.__raw_target
            )

        for template_name in raw_target.data.get("target", {}).get("inherit", []):
            if template_name not in suit.templates:
                raise ValueError(f"Template {template_name!r} not found")
            for script_name, value in suit.templates[template_name].get("scripts", {}).items():
                scripts[script_name] = TargetScript.compile_inline(
                    value, self.__suit, self.__raw_target
                )

        self.__scripts = scripts

    @property
    def name(self) -> str:
        return self.__name

    @property
    def scripts(self) -> Mapping[str, Any]:
        return self.__scripts


class TargetScript(NamedTuple):
    cmd: str
    root: Box
    local: Box
    args: Box

    @staticmethod
    def compile_inline(
        raw_cmd: str, suit: Suit, raw_target: _TargetConfig
    ) -> TargetScript:
        return TargetScript(
            cmd=raw_cmd,
            root=Box(
                path=suit.root,
            ),
            local=Box(
                path=raw_target.path,
            ),
            args=Box(),
        )

    def execute(self) -> ScriptExecution:
        return ScriptExecution(
            Popen(
                shlex.split(
                    self.cmd.format(root=self.root, local=self.local, args=self.args)
                ),
                stdout=PIPE,
                stderr=PIPE,
            )
        )


class Targets(Mapping[str, Target]):
    def __init__(
        self,
        suit_ref: weakref.ReferenceType[Suit],
    ):
        self.__suit_ref = suit_ref

        suit = self.__follow_suit_ref()
        self.__canonized = {
            str(raw_target.path.relative_to(suit.root)): raw_target
            for raw_target in suit.raw_targets
        }

    def __follow_suit_ref(self) -> Suit:
        if not (suit := self.__suit_ref()):
            raise ValueError("Provided suit reference invalid")
        return suit

    def __getitem__(self, __k: str) -> Target:
        return Target(__k, self.__follow_suit_ref(), self.__canonized[__k])

    def __iter__(self) -> Iterator[str]:
        return iter(self.__canonized)

    def __len__(self) -> int:
        return len(self.__canonized)

    def find(self, pattern: str) -> Iterable[Target]:
        re_pattern = re.compile(pattern)
        return (
            Target(
                name,
                self.__follow_suit_ref(),
                self.__canonized[name],
            )
            for name in self.__canonized
            if re_pattern.search(name)
        )


class ScriptExecution:
    def __init__(self, process: Popen):
        self.__process = process
        self.__stdout = self.__process.stdout
        self.__stderr = self.__process.stderr

    @property
    def stdout(self) -> IO[AnyStr]:
        return cast(IO[AnyStr], self.__stdout)

    @property
    def stderr(self):
        return cast(IO[AnyStr], self.__stderr)
