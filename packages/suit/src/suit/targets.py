from __future__ import annotations

import abc
import pathlib
from dataclasses import dataclass, field
from typing import Any, List, Mapping, Optional, Union


class ScriptSpec(metaclass=abc.ABCMeta):
    pass


@dataclass
class ShellScriptSpec(ScriptSpec):
    cmd: str
    args: Mapping[str, Any] = field(default_factory=dict)


@dataclass
class ScriptRefSpec(ScriptSpec):
    ref: str
    args: Mapping[str, Any] = field(default_factory=dict)


@dataclass
class CompositeScriptSpec(ScriptSpec):
    scripts: List[ScriptSpec]
    args: Mapping[str, Any] = field(default_factory=dict)


def _process_scripts(scripts: Optional[Mapping[str, Union[str, Mapping[str, Any], ScriptSpec]]]):
    if not scripts:
        return {}
    processed_scripts = {}
    for script_name, script_input in scripts.items():
        if isinstance(script_input, (ScriptSpec)):
            processed_scripts[script_name] = script_input
            continue

        if isinstance(script_input, str):
            processed_scripts[script_name] = ShellScriptSpec(script_input, {})
            continue

        if "cmd" in script_input and isinstance(script_input["cmd"], str):
            processed_scripts[script_name] = ShellScriptSpec(script_input["cmd"], script_input.get("args", {}))
            continue

        if "ref" in script_input and isinstance(script_input["ref"], str):
            processed_scripts[script_name] = ScriptRefSpec(script_input["ref"], script_input.get("args", {}))
            continue

        raise ValueError(script_input)

    return processed_scripts


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

        object.__setattr__(self, "scripts", _process_scripts(scripts))


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
