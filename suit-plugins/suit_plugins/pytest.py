from suit import Runtime, Scope


class pytest:
    def __init__(self, location: str, *, color="auto"):
        self.__location = location
        self.__color = color

    def __call__(self, runtime: Runtime, scope: Scope):
        with runtime.ui_panel("pytest"):
            res = runtime.shell(
                [
                    "pytest",
                    str(scope.local / self.__location),
                    f"--color={self.__color}",
                ]
            )
            if res.returncode != 0:
                runtime.error(res.stdout)
                runtime.fail(f"Pytest failed (return code {res.returncode})")
            else:
                runtime.info(res.stdout)
