import subprocess

from rich.panel import Panel
from rich.status import Status

from suit import Runtime, Scope, suit


@suit("lint")
def target_lint(runtime: Runtime, scope: Scope):
    runtime.log("Linting using `black`...")
    res = runtime.shell(["black", "--check", str(scope.local / "suit")])
    runtime.log(Panel(res.stderr.decode("utf-8").strip(), title="`black` [b red]errors![/]"))
