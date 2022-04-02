import functools

from decorator import decorator

from suit import Runtime, Scope, suit


class _FnPlugin:

    def __init__(self, fn, name):
        self.__fn = fn
        self.__name = name

    def __call__(self, *args, **kwargs):
        return suit(self.__name)(functools.partial(self.__fn, *args, **kwargs))


def plugin(name, func=None):
    if func:
        return _FnPlugin(func, name)

    def _tmp(func):
        return _FnPlugin(func, name)

    return _tmp
