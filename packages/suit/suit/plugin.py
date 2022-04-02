import abc
import functools


class PluginBase(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def _execute(self, *args, **kwargs):
        raise NotImplementedError

    def __call__(self, *args, **kwargs):
        return functools.partial(self._execute, *args, **kwargs)


class _FnPlugin(PluginBase):

    def __init__(self, fn):
        self.__fn = fn

    def _execute(self, *args, **kwargs):
        return self.__fn(*args, **kwargs)


class _PartialBuilder:

    def __init__(self, fn):
        self.__fn = fn

    def __call__(self, *args, **kwargs):
        return functools.partial(self.__fn, *args, **kwargs)


def plugin(fn):
    return _PartialBuilder(fn)
