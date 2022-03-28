import contextlib
import logging
import pathlib
import shlex
import subprocess
from datetime import datetime
from typing import Iterable, List, Optional, Tuple, Union

import arrow
import rich.console
import rich.logging
from rich.console import Group, RenderableType
from rich.live import Live
from rich.padding import Padding
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


def _format_time(dt: datetime) -> Text:
    return Text.assemble(f"[{arrow.get(dt).format('YYYY-MM-DD HH:mm:ss')}]")


class _PrintGroup:
    def __init__(self, title: Union[str, Text]):
        self.__title = title
        self.__renderables = []

    def print(self, *renderables):
        self.__renderables += renderables

    def __rich__(self):
        grid = Table.grid(padding=(0, 1, 0, 0))
        row_content: List[RenderableType] = [Text(f"[{arrow.utcnow().format('YYYY-MM-DD HH:mm:ss')}]", "dim cyan")]
        if self.__renderables:
            row_content.append(Panel(Group(*self.__renderables), title=self.__title))
        grid.add_row(*row_content)
        return grid


class Runtime:

    def __init__(self, cwd: Optional[pathlib.Path] = None):
        if not cwd:
            cwd = pathlib.Path.cwd()
        self.cwd = cwd

        self.console = rich.console.Console(log_time_format=_format_time)
        self.status = self.console.status
        self.print = self.console.log
        self.__logger = logging.getLogger("suit.core")
        self.__logger.addHandler(
            rich.logging.RichHandler(
                console=self.console,
                markup=True,
                rich_tracebacks=True,
                tracebacks_show_locals=True,
                log_time_format=_format_time,
            ))

        self.info = self.__logger.info
        self.debug = self.__logger.debug
        self.error = self.__logger.error
        self.warn = self.__logger.warn

    def shell(self, command: Union[str, List[str], Tuple[str, ...]]):
        if isinstance(command, str):
            command = shlex.split(command)
        return subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def fail(self, message: str):
        raise TargetFailedException(message)

    @contextlib.contextmanager
    def _set_message_group(self, title: Union[str, Text]):
        content_window = _PrintGroup(title)
        with Live(content_window, console=self.console, refresh_per_second=2):
            self.print = content_window.print
            yield
        self.print = self.console.print


class TargetFailedException(Exception):
    pass
