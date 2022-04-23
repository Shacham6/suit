from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Any, Mapping, Generic, TypeVar
from suit.targets import ShellScriptSpec, TargetConfig
from suit.collector import SuitConfig

_T = TypeVar("_T")


@dataclass(kw_only=True)
class _ScriptBase(Generic[_T], metaclass=abc.ABCMeta):
    name: str
    specs: _T
    suit: SuitConfig
    target: TargetConfig

    @abc.abstractmethod
    def accept(self, executor: ScriptExecutor):
        raise NotImplementedError


class ScriptExecutor(metaclass=abc.ABCMeta):
    def execute(self, script: _ScriptBase):
        return script.accept(self)

    @abc.abstractmethod
    def handle_shell_script(self, shell_script: ShellScript):
        raise NotImplementedError


@dataclass
class ShellScript(_ScriptBase[ShellScriptSpec]):
    def accept(self, executor: ScriptExecutor):
        return executor.handle_shell_script(self)
