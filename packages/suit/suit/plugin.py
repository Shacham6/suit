import functools

from decorator import decorator

from suit import Runtime, Scope, suit


class _FnPlugin:

    def __init__(self, fn, name):
        self.__fn = fn
        self.__name = name

    def __call__(self, *args, **kwargs):
        return suit(self.__name)(functools.partial(self.__fn, *args, **kwargs))


@decorator
def plugin(func, name):
    return _FnPlugin(func, name)
