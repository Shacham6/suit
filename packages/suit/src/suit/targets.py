from __future__ import annotations

import abc
import pathlib
from dataclasses import dataclass, field
from typing import Any, List, Mapping, Optional, Tuple, Union

from suit.scripts.specs import ScriptSpec, scripts_from_mapping


@dataclass(init=False, frozen=True)
class TargetConfigData:
    inherit: List[str]
    args: Mapping[str, Any]
    scripts: Mapping[str, ScriptSpec]

    def __init__(
        self,
        inherit: Optional[List[str]] = None,
        args: Optional[Mapping[str, Any]] = None,
        scripts: Optional[Mapping[str, Union[str, Mapping[str, Any], ScriptSpec]]] = None,
    ):
        # Setting objects is weird on frozen dataclasses.
        if not inherit:
            inherit = []
        object.__setattr__(self, "inherit", inherit)

        if not args:
            args = {}
        object.__setattr__(self, "args", args)

        object.__setattr__(self, "scripts", scripts_from_mapping(scripts))


@dataclass
class TargetConfig:
    """
    A project target.
    """

    path: pathlib.Path
    data: TargetConfigData

    @staticmethod
    def from_mapping(path: pathlib.Path, data: Mapping[str, Any]) -> TargetConfig:
        """Build a `TargetConfig` from raw, mapping data."""
        return TargetConfig(path=path, data=TargetConfigData(**data))
