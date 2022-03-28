from datetime import datetime

import arrow
from rich.console import Console
from rich.panel import Panel
from rich.text import Text


def __format_time(dt: datetime) -> Text:
    return Text.assemble(f"[{arrow.get(dt).format('YYYY-MM-DD HH:mm:ss')}]")


console = Console(log_time_format=__format_time)
console.log("[green]INFO[/]", Panel("This is great"))
