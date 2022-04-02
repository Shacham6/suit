from typing import Callable, Protocol, TypeVar

from typing_extensions import ParamSpec

from suit import Runtime, Scope, SuitTarget, suit

_P = ParamSpec("_P")
_R = TypeVar("_R")


class PluginFn(Protocol[_P]):
    def __call__(self, *args: _P.args, **kwargs: _P.kwargs):
        ...


class _FnPlugin:
    def __init__(self, fn: PluginFn, name: str):
        self.__fn = fn
        self.__name = name

    def __call__(self, *args, **kwargs) -> SuitTarget:
        @suit(self.__name)
        def _suit_obj(runtime: Runtime, scope: Scope):
            return self.__fn(*args, **kwargs, runtime=runtime, scope=scope)

        return _suit_obj


def plugin(name: str) -> Callable[[PluginFn], _FnPlugin]:
    def _tmp(func):
        return _FnPlugin(func, name)

    return _tmp
