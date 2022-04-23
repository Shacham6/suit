from __future__ import annotations

import abc
import pathlib
from dataclasses import dataclass, field
from typing import Any, List, Mapping, Optional, Tuple, Union


class ScriptSpec(metaclass=abc.ABCMeta):
    pass


@dataclass
class ShellScriptSpec(ScriptSpec):
    cmd: str
    args: Mapping[str, Any] = field(default_factory=dict)


@dataclass
class RefScriptSpec(ScriptSpec):
    ref: str
    args: Mapping[str, Any] = field(default_factory=dict)


@dataclass
class CompositeScriptSpec(ScriptSpec):
    scripts: List[ScriptSpec]
    args: Mapping[str, Any] = field(default_factory=dict)


def _process_scripts(scripts: Optional[Mapping[str, Union[str, Mapping[str, Any], ScriptSpec]]]):
    if not scripts:
        return {}

    return {script_name: _process_script(script_input) for script_name, script_input in scripts.items()}


def _process_script(
    script_input: Union[
        str,
        List[str],
        Tuple[str, ...],
        Mapping[str, Any],
        ScriptSpec,
    ]
) -> ScriptSpec:
    if isinstance(script_input, ScriptSpec):
        return script_input

    if isinstance(script_input, str):
        return ShellScriptSpec(script_input, {})

    if isinstance(script_input, (list, tuple)):
        return CompositeScriptSpec([_process_script(inner) for inner in script_input])

    if "cmd" in script_input and isinstance(script_input["cmd"], str):
        return ShellScriptSpec(script_input["cmd"], script_input.get("args", {}))

    if "ref" in script_input and isinstance(script_input["ref"], str):
        return RefScriptSpec(script_input["ref"], script_input.get("args", {}))

    if "scripts" in script_input and isinstance(script_input["scripts"], (list, tuple)):
        return CompositeScriptSpec(
            [_process_script(inner) for inner in script_input["scripts"]],
            script_input.get("args", {}),
        )

    raise ValueError(script_input)


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
