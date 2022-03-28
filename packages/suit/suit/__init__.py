from __future__ import annotations

import pathlib
from dataclasses import dataclass
from typing import List, Optional, Protocol, runtime_checkable

import rich.repr

from suit.runtime import Runtime


@rich.repr.auto()
class _SuitRegistry:

    def __init__(self, suits: Optional[List[SuitTarget]] = None):
        if not suits:
            suits = []
        self.__suits = suits

    @property
    def suits(self) -> List[SuitTarget]:
        return self.__suits

    def add(self, suit: SuitTarget) -> None:
        self.__suits.append(suit)

    def __rich_repr__(self):
        yield "suits", self.suits


registered = _SuitRegistry()


@dataclass(frozen=True)
class Scope:
    target: str
    local: pathlib.Path
    root: pathlib.Path


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


def suit(target_name: str):

    def __tmp(func):
        target = SuitTarget(target_name, func)
        registered.add(target)
        return target

    return __tmp
