from __future__ import annotations

import contextlib
import shlex
import subprocess
from datetime import datetime
from typing import Callable, List, Tuple, Union

import arrow
import logbook
import rich.console
import rich.logging
import rich.traceback
from box import Box
from rich.console import Group, RenderableType
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .scope import Scope


def _format_time(dt: datetime) -> Text:
    return Text.assemble(f"[{arrow.get(dt).format('YYYY-MM-DD HH:mm:ss')}]")


console = rich.console.Console(log_time_format=_format_time)
rich.traceback.install(console=console)


class RicherHandler(logbook.Handler):
    def emit(self, record: logbook.LogRecord):
        g = Table.grid(padding=(0, 1))
        g.add_row(
            Text.assemble(
                "[",
                (arrow.get(record.time).format("YYYY-MM-DD HH:mm:ss"), "dim cyan"),
            ),
            "|",
            record.extra.get("scope", "[b]root[/]"),
            "|",
            Text.assemble(
                (f"{record.level_name:<8}", self._level_style(record.level_name))
            ),
            "| ",
            str(record.message)
            if isinstance(record.message, Exception)
            else record.message,
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
    def __init__(self, scope: Scope, config: Box):
        self.scope = scope
        self.__logger = logbook.Logger("suit")
        self.info = self.__logger.info
        self.debug = self.__logger.debug
        self.warn = self.__logger.warn
        self.error = self.__logger.error
        self.exception = self.__logger.exception
        self.config = config

    def shell(self, command: Union[str, List[str], Tuple[str, ...]]):
        if isinstance(command, str):
            command = shlex.split(command)
        return subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8"
        )

    def fail(self, message: str):
        raise TargetFailedException(message)

    @contextlib.contextmanager
    def ui_panel(self, title: str):
        live_controller = Live()
        ui_panel = UIPanel(title, lambda renderable: live_controller.update(renderable))
        ui_panel_handler = UIPanelHandler(ui_panel)
        with ui_panel_handler, live_controller:
            yield ui_panel


class UIPanelHandler(logbook.Handler):
    def __init__(self, live: UIPanel):
        super().__init__()
        self.__ui_panel = live

    def emit(self, record: logbook.LogRecord):
        g = Table.grid(padding=(0, 1))
        g.add_row(
            Text.assemble(
                "[",
                (arrow.get(record.time).format("YYYY-MM-DD HH:mm:ss"), "dim cyan"),
            ),
            "| ",
            str(record.message)
            if isinstance(record.message, Exception)
            else record.message,
        )
        self.__ui_panel.set_level(record.level_name.upper())
        self.__ui_panel.set_scope(record.extra.get("scope", "[b]root[/]"))
        self.__ui_panel.push(g)

    def _level_style(self, level_name: str) -> str:
        return {
            "INFO": "bold",
            "DEBUG": "bold cyan",
            "ERROR": "bold red",
            "CRITICAL": "bold red",
        }[level_name.upper()]


class UIPanel:
    def __init__(self, title: str, on_update: Callable[[RenderableType], None]):
        self.__title = title
        self.__creation_time = arrow.now()
        self.__renderables = []
        self.__scope = ""
        self.__level = "DEBUG"
        self.__on_update = on_update

    def push(self, renderable: RenderableType):
        self.__renderables.append(renderable)
        self.__on_update(self)

    def set_scope(self, scope: str):
        self.__scope = scope
        return self

    def set_level(self, level: str):
        self.__level = level
        return self

    def __rich__(self) -> RenderableType:
        g = Table.grid(padding=(0, 1))
        g.add_row(
            Text.assemble(
                "[",
                (self.__creation_time.format("YYYY-MM-DD HH:mm:ss"), "dim cyan"),
            ),
            "|",
            self.__scope,
            "|",
            Text.assemble((f"{self.__level:<8}", self._level_style(self.__level))),
            "| ",
            Panel(
                Group(*self.__renderables),
                title=Text(self.__title, "bold"),
                title_align="left",
            ),
        )
        return g

    def _level_style(self, level_name: str) -> str:
        return {
            "INFO": "bold",
            "DEBUG": "bold cyan",
            "ERROR": "bold red",
            "CRITICAL": "bold red",
        }[level_name.upper()]


class TargetFailedException(Exception):
    pass
