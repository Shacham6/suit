import pathlib
import signal
import subprocess

from rich.text import Text
from suit import Runtime, Scope


class InstallRequires:
    def __init__(self, requires_file: str):
        self.__requires_file = requires_file

    def __call__(self, runtime: Runtime, scope: Scope):
        requires_file = str(scope.local / self.__requires_file)
        pip_install_process = subprocess.Popen(
            ["pip", "install", "-r", requires_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(scope.local),
            encoding="utf-8",
        )
        runtime.info("Installing requirements...")

        try:
            if pip_install_process.stdout:
                for line in pip_install_process.stdout:
                    runtime.info(
                        Text.assemble(
                            ("OUTPUT|", "dim cyan"),
                            " ",
                            (line.rstrip("\n"), "italic"),
                        )
                    )

            if pip_install_process.stderr:
                for line in pip_install_process.stderr:
                    runtime.error(
                        Text.assemble(
                            ("ERROR|", "dim red"),
                            " ",
                            (line.rstrip("\n"), "italic"),
                        )
                    )

        except KeyboardInterrupt:
            pip_install_process.send_signal(signal.SIGKILL)


def __fix_lines(sources):
    for name, source in sources:
        for line in source:
            line = line.rstrip("\n")
