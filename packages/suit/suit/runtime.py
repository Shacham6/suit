import pathlib
from datetime import datetime

import arrow
import rich.console
from rich.text import Text


def _format_time(dt: datetime) -> Text:
    return Text.assemble(f"[{arrow.get(dt).format('YYYY-MM-DD HH:mm:ss')}]")


class Runtime:

    def __init__(self):
        self.cwd = pathlib.Path.cwd()
        self.console = rich.console.Console(log_time_format=_format_time)
        self.log = self.console.log
