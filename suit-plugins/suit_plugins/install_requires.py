import pathlib
import subprocess

from suit import Runtime, Scope


class InstallRequires:
    def __init__(self, requires_file: str):
        self.__requires_file = requires_file

    def __call__(self, runtime: Runtime, scope: Scope):
        requires_file = str(scope.local / self.__requires_file)
        subprocess.call(["pip", "install", "-r", requires_file])
