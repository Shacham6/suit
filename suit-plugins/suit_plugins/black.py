from rich.panel import Panel
from suit import Runtime, Scope, suit
from suit.plugin import plugin


def lint(location: str):

    @suit("lint")
    def impl(runtime: Runtime, scope: Scope):
        runtime.info("Linting using `black`...")
        res = runtime.shell(["black", "--check", str(scope.local / location)])
        if res.returncode != 0:
            __print_process_error(runtime, res)
        runtime.info("Finished linting using `black`.")

    return impl


@plugin("format")
def format_(location: str, *, runtime: Runtime, scope: Scope):
    runtime.info("Formatting using `black`...")
    res = runtime.shell(["black", str(scope.local / location)])
    if res.stdout:
        runtime.info(Panel(res.stdout.decode("utf-8"), title="`black` output"))
    if res.returncode != 0:
        __print_process_error(runtime, res)
    runtime.info("Finished formatting using `black`.")


def __print_process_error(runtime, process):
    err_message = process.stderr.decode("utf-8").strip()
    runtime.error(Panel(err_message, title="`black` [b red]errors[/]!"))
    runtime.fail("`black` returned with non-zero return code.")
