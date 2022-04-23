from __future__ import annotations

import pathlib
from dataclasses import dataclass, field
from typing import Any, List, Mapping, Optional, Union


@dataclass
class ShellScriptSpec:
    cmd: str
    args: Mapping[str, Any] = field(default_factory=dict)


@dataclass
class CompositeScriptSpec:
    scripts: List[ScriptSpec]
    args: Mapping[str, Any] = field(default_factory=dict)


ScriptSpec = Union[CompositeScriptSpec, ShellScriptSpec]


def _process_scripts(scripts: Optional[Mapping[str, Union[str, Mapping[str, Any], ScriptSpec]]]):
    if not scripts:
        return {}
    processed_scripts = {}
    for script_name, script_input in scripts.items():
        if isinstance(script_input, ScriptSpec):
            processed_scripts[script_name] = script_input
            continue

        processed_scripts[script_name] = _build_script(script_input)
    return processed_scripts


def _build_script(script_data: Union[str, Mapping[str, Any]]):
    if isinstance(script_data, str):
        return ShellScriptSpec(script_data, {})
    if "cmd" in script_data and isinstance(script_data["cmd"], str):
        return ShellScriptSpec(script_data["cmd"], script_data.get("args", {}))
    raise ValueError(f"Can't build script from {script_data}")


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
