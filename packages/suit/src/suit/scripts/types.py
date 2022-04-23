from __future__ import annotations

import abc
from dataclasses import dataclass


class _ScriptBase(metaclass=abc.ABCMeta):
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
    def handle_composite_script(self, composite_script: CompositeScript):
        raise NotImplementedError


@dataclass
class ShellScript(_ScriptBase):
    cmd: str

    def accept(self, visitor: ScriptExecutor):
        return visitor.handle_shell_script(self)


@dataclass
class CompositeScript(_ScriptBase):
    def accept(self, executor: ScriptExecutor):
        return super().accept(executor)
