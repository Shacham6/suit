import logging
import pathlib
import shlex
import subprocess
from datetime import datetime
from typing import Iterable, List, Optional, Tuple, Union

import arrow
import rich.console
import rich.logging
from rich.text import Text


def _format_time(dt: datetime) -> Text:
    return Text.assemble(f"[{arrow.get(dt).format('YYYY-MM-DD HH:mm:ss')}]")


class Runtime:

    def __init__(self, cwd: Optional[pathlib.Path] = None):
        if not cwd:
            cwd = pathlib.Path.cwd()
        self.cwd = cwd

        self.console = rich.console.Console(log_time_format=_format_time, stderr=True)
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


class TargetFailedException(Exception):
    pass
