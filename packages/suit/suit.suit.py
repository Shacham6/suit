import subprocess

from rich.panel import Panel
from rich.status import Status

from suit import Runtime, Scope, suit


@suit("lint")
def target_lint(runtime: Runtime, scope: Scope):
    runtime.debug("Linting using `black`...")
    res = runtime.shell(["black", "--check", str(scope.local / "suit")])
    if res.returncode != 0:
        runtime.print(Panel(res.stderr.decode("utf-8").strip(), title="`black` [b red]errors![/]"))
        res.check_returncode()
        # res.check_returncode()
