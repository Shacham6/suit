from __future__ import annotations

import importlib
import importlib.metadata
from typing import List, Optional
import rich.repr


@rich.repr.auto()
class _SuitRegistry:

    def __init__(self, suits: Optional[List[_SuitTarget]] = None):
        if not suits:
            suits = []
        self.__suits = suits

    @property
    def suits(self) -> List[_SuitTarget]:
        return self.__suits

    def add(self, suit: _SuitTarget) -> None:
        self.__suits.append(suit)

    def __rich_repr__(self):
        yield "suits", self.suits


registered = _SuitRegistry()


@rich.repr.auto()
class _SuitTarget:

    def __init__(self, name: str, fn):
        self.__name = name
        self.__fn = fn

    @property
    def name(self) -> str:
        return self.__name

    @property
    def fn(self):
        return self.__fn

    def invoke(self, runtime):
        self.__fn(runtime)

    def __rich_repr__(self):
        yield "name", self.__name


def suit(target_name: str):

    def __tmp(func):
        target = _SuitTarget(target_name, func)
        registered.add(target)
        return target

    return __tmp
