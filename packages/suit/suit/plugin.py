from suit import Runtime, Scope, suit


class _FnPlugin:
    def __init__(self, fn, name):
        self.__fn = fn
        self.__name = name

    def __call__(self, *args, **kwargs):
        @suit(self.__name)
        def _suit_obj(runtime: Runtime, scope: Scope):
            return self.__fn(*args, **kwargs, runtime=runtime, scope=scope)

        return _suit_obj


def plugin(name, func=None):
    if func:
        return _FnPlugin(func, name)

    def _tmp(func):
        return _FnPlugin(func, name)

    return _tmp
