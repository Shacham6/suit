from __future__ import annotations

import pathlib
from typing import List, Mapping

import rich.repr
from pydantic import BaseModel, Field, validator  # pylint: disable=no-name-in-module

from suit.scripts.specs import scripts_from_mapping

from .targets import ScriptSpec, TargetConfig


class SuitTemplate(BaseModel):
    scripts: Mapping[str, ScriptSpec]

    @validator("scripts", pre=True)
    def validate_scripts(cls, v):
        return scripts_from_mapping(v)

    # @classmethod
    # def __get_validators__(cls):
    #     yield scripts_from_mapping

    class Config:
        arbitrary_types_allowed = True


class ProjectConfig(BaseModel):
    templates: Mapping[str, SuitTemplate] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True


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
