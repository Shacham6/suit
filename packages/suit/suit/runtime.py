import contextlib
import logging
import pathlib
import shlex
import subprocess
from datetime import datetime
from typing import Iterable, List, Optional, Tuple, Union

import arrow
import logbook
import rich.console
import rich.logging
import rich.traceback
from rich.console import Group, RenderableType
from rich.live import Live
from rich.padding import Padding
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.traceback import Traceback

from .scope import Scope


def _format_time(dt: datetime) -> Text:
    return Text.assemble(f"[{arrow.get(dt).format('YYYY-MM-DD HH:mm:ss')}]")


class _PrintGroup:

    def __init__(self, title: Union[str, Text]):
        self.__title = title
        self.__renderables = []

    def print(self, renderable):
        self.__renderables.append(renderable)

    def __rich__(self):
        grid = Table.grid(padding=(0, 1, 0, 0))
        row_content: List[RenderableType] = [Text(f"[{arrow.utcnow().format('YYYY-MM-DD HH:mm:ss')}]", "dim cyan")]
        if self.__renderables:
            row_content.append(Panel(Group(*self.__renderables), title=self.__title))
        grid.add_row(*row_content)
        return grid


console = rich.console.Console(log_time_format=_format_time)
rich.traceback.install(console=console)


class RicherHandler(logbook.Handler):

    def emit(self, record: logbook.LogRecord):
        # if isinstance(record.message, Exception):
        #     return
        g = Table.grid(padding=(0, 1))
        g.add_row(
            Text.assemble(
                "[",
                (arrow.get(record.time).format("YYYY-MM-DD HH:mm:ss"), "dim cyan"),
            ),
            "|",
            record.extra.get("scope", "[b]root[/]"),
            "|",
            Text.assemble((f"{record.level_name:<8}", self._level_style(record.level_name))),
            "]",
            str(record.message) if isinstance(record.message, Exception) else record.message,
        )
        console.print(g)

    def _level_style(self, level_name: str) -> str:
        return {
            "INFO": "bold",
            "DEBUG": "bold cyan",
            "ERROR": "bold red",
            "CRITICAL": "bold red",
        }[level_name.upper()]


RicherHandler().push_application()


class Runtime:

    def __init__(self, scope: Scope):
        self.scope = scope
        self.__logger = logbook.Logger("suit")
        self.info = self.__logger.info
        self.debug = self.__logger.debug
        self.warn = self.__logger.warn
        self.error = self.__logger.error
        self.exception = self.__logger.exception

    def shell(self, command: Union[str, List[str], Tuple[str, ...]]):
        if isinstance(command, str):
            command = shlex.split(command)
        return subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def fail(self, message: str):
        raise TargetFailedException(message)


class TargetFailedException(Exception):
    pass
