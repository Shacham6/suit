import pathlib
import shlex
import subprocess
from datetime import datetime
from typing import Iterable, List, Optional, Tuple, Union

import arrow
import rich.console
from rich.text import Text


def _format_time(dt: datetime) -> Text:
    return Text.assemble(f"[{arrow.get(dt).format('YYYY-MM-DD HH:mm:ss')}]")


class Runtime:

    def __init__(self, cwd: Optional[pathlib.Path] = None):
        if not cwd:
            cwd = pathlib.Path.cwd()
        self.cwd = cwd

        self.console = rich.console.Console(log_time_format=_format_time)
        self.log = self.console.log

    def shell(self, command: Union[str, List[str], Tuple[str, ...]]):
        if isinstance(command, str):
            command = shlex.split(command)
        return subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
