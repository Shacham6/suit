import subprocess

import suit_plugins.black
from rich.panel import Panel
from rich.status import Status

from suit import Runtime, Scope, suit

lint = suit_plugins.black.lint
format_ = suit_plugins.black.format_
