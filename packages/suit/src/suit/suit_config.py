from __future__ import annotations

import pathlib
from typing import Any, List, Mapping

import rich.repr
from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module

from .targets import TargetConfig


class SuitTemplate(BaseModel):
    pass


class ProjectConfig(BaseModel):
    templates: Mapping[str, SuitTemplate] = Field(default_factory=dict)


@rich.repr.auto()
class SuitConfig:
    """
    The general suit configurations.
    """

    def __init__(
        self,
        root: pathlib.Path,
        project_config: ProjectConfig,
        targets: List[TargetConfig],
    ):
        self.__root = root
        self.__project_config = project_config
        self.__targets = {str(target.path.relative_to(root)): target for target in targets}

    @property
    def root(self) -> pathlib.Path:
        return self.__root

    @property
    def project_config(self) -> ProjectConfig:
        return self.__project_config

    @property
    def targets(self) -> Mapping[str, TargetConfig]:
        return self.__targets

    def __rich_repr__(self) -> rich.repr.RichReprResult:
        yield "root", self.__root
        yield "project_config", self.__project_config
        yield "targets", self.__targets
