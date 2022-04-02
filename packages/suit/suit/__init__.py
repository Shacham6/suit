from __future__ import annotations

from typing import List, Optional, Protocol, runtime_checkable

import rich.repr

from suit.runtime import Runtime

from .scope import Scope


@runtime_checkable
class TargetFn(Protocol):
    def __call__(self, runtime: Runtime, scope: Scope):
        ...


@rich.repr.auto()
class SuitTarget:
    def __init__(self, name: str, fn: TargetFn):
        self.__name = name
        self.__fn = fn

    @property
    def name(self) -> str:
        return self.__name

    @property
    def fn(self) -> TargetFn:
        return self.__fn

    def invoke(self, runtime, scope: Scope):
        return self.__fn(runtime, scope)

    def __rich_repr__(self):
        yield "name", self.__name


def suit(target_name: str, func=None):
    if func:
        return SuitTarget(target_name, func)

    def __tmp(func):
        target = SuitTarget(target_name, func)
        return target

    return __tmp
