import pathlib
from typing import Any, Mapping, NamedTuple


class TargetsCollector:
    def __init__(self, root: pathlib.Path):
        self.__root = root

    def collect(self):
        return [
            Target()
        ]


class Target:
    pass


def _pyproject_uses_suit(pyproject_data: Mapping[str, Any]) -> bool:
    if "suit" not in pyproject_data.get("tool", {}):
        return False
    return True
