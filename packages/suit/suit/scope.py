import pathlib
from dataclasses import dataclass


@dataclass(frozen=True)
class Scope:
    target: str
    local: pathlib.Path
    root: pathlib.Path
