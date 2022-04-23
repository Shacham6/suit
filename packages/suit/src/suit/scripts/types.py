from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Any, Generic, Mapping, TypeVar

from suit.collector import SuitConfig
from suit.targets import TargetConfig

from .specs import CompositeScriptSpec, RefScriptSpec, ShellScriptSpec

_T = TypeVar("_T")


@dataclass
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

    @abc.abstractmethod
    def handle_ref_script(self, ref_script: RefScript):
        raise NotImplementedError

    @abc.abstractmethod
    def handle_composite_script(self, composite_script: CompositeScript):
        raise NotImplementedError


@dataclass
class ShellScript(_ScriptBase[ShellScriptSpec]):
    def accept(self, executor: ScriptExecutor):
        return executor.handle_shell_script(self)


@dataclass
class RefScript(_ScriptBase[RefScriptSpec]):
    def accept(self, executor: ScriptExecutor):
        return executor.handle_ref_script(self)


@dataclass
class CompositeScript(_ScriptBase[CompositeScriptSpec]):
    def accept(self, executor: ScriptExecutor):
        return executor.handle_composite_script(self)
