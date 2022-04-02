from rich.panel import Panel
from suit import Runtime, Scope


class lint:
    def __init__(self, location: str):
        self.__location = location

    def __call__(self, runtime: Runtime, scope: Scope):
        runtime.info("Linting using `black`...")
        res = runtime.shell(["black", "--check", str(scope.local / self.__location)])
        if res.returncode != 0:
            _print_process_error(runtime, res)
        runtime.info("Finished linting using `black`.")


class format_:
    def __init__(self, location: str):
        self.__location = location

    def __call__(self, runtime: Runtime, scope: Scope):
        runtime.info("Formatting using `black`...")
        res = runtime.shell(["black", str(scope.local / self.__location)])
        if res.stdout:
            runtime.info(Panel(res.stdout.decode("utf-8"), title="`black` output"))
        if res.returncode != 0:
            _print_process_error(runtime, res)
        runtime.info("Finished formatting using `black`.")


def _print_process_error(runtime, process):
    err_message = process.stderr.decode("utf-8").strip()
    runtime.error(Panel(err_message, title="`black` [b red]errors[/]!"))
    runtime.fail("`black` returned with non-zero return code.")
