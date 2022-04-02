import subprocess

from rich.panel import Panel
from rich.status import Status

from suit import Runtime, Scope, suit
import suit_plugins.black

lint = suit_plugins.black.lint

# @suit("lint2")
# def lint2(runtime: Runtime, scope: Scope):
#     runtime.info("Linting using `black`...")
#     res = runtime.shell(["black", "--check", str(scope.local / "suit")])
#     if res.returncode != 0:
#         err_message = res.stderr.decode("utf-8").strip()
#         runtime.error(Panel(err_message, title="`black` [b red]errors[/]!"))
#         runtime.fail("`black` returned with non-zero return code.")
