from __future__ import annotations

import pathlib
from typing import Any, List, Mapping

import rich.repr

from .targets import TargetConfig


@rich.repr.auto()
class SuitConfig:
    """
    The general suit configurations.
    """

    def __init__(
        self,
        root: pathlib.Path,
        project_config: Mapping[str, Any],
        targets: List[TargetConfig],
    ):
        self.__root = root
        self.__project_config = project_config
        self.__targets = {str(target.path.relative_to(root)): target for target in targets}
        self.__templates = project_config.get("templates", {})

    @property
    def root(self) -> pathlib.Path:
        return self.__root

    @property
    def project_config(self) -> Mapping[str, Any]:
        return self.__project_config

    @property
    def targets(self) -> Mapping[str, TargetConfig]:
        return self.__targets

    @property
    def templates(self) -> Mapping[str, Any]:
        return self.__templates

    def __rich_repr__(self) -> rich.repr.RichReprResult:
        yield "root", self.__root
        yield "project_config", self.__project_config
        yield "targets", self.__targets
