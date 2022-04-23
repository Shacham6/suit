import shlex
from subprocess import PIPE, Popen

from box import Box
from rich.text import Text
from suit.console import console
from suit.scripts.types import CompositeScript, RefScript, ScriptExecutor, ShellScript
from suit.scripts.resolver import resolve_scripts, resolve_script


class CLIExecutor(ScriptExecutor):
    def __init__(self, is_dry_run: bool):
        self.__is_dry_run = is_dry_run

    def handle_shell_script(self, shell_script: ShellScript):
        target_name = str(shell_script.target.path.relative_to(shell_script.suit.root))
        console.log(
            Text.assemble(
                "Will run '", Text.assemble(target_name, ":", shell_script.name, style="yellow italic"), "'..."
            )
        )
        if self.__is_dry_run:
            return

        full_command = shell_script.specs.cmd.format(
            root=Box(path=shell_script.suit.root),
            local=Box(path=shell_script.target.path),
            args=Box(shell_script.target.data.args),
        )
        process = Popen(shlex.split(full_command), encoding="utf-8", stdout=PIPE, stderr=PIPE)
        return_code = process.wait()
        for out_line in process.stdout:
            out_text = Text.assemble(
                ("OUT | ", "bold"),
                out_line.rstrip("\n"),
            )
            out_text.pad_left(4)
            console.log(out_text)

        for err_line in process.stderr:
            err_text = Text.assemble(
                ("ERR | ", "red bold"),
                err_line.rstrip("\n"),
            )
            err_text.pad_left(4)
            console.log(err_text)

        if return_code != 0:
            console.log(f"[red]Target script exited with return-code [bold]{return_code}[/][/]")
            raise ScriptFailedError(target_name, shell_script.name, return_code)

    def handle_ref_script(self, ref_script: RefScript):
        scripts = resolve_scripts(ref_script.suit, ref_script.target)
        self.execute(scripts[ref_script.specs.ref])

    def handle_composite_script(self, composite_script: CompositeScript):
        for index, raw_script in enumerate(composite_script.specs.scripts):
            script = resolve_script(
                composite_script.suit, composite_script.target, f"{composite_script.name}[{index}]", raw_script
            )
            self.execute(script)


class ScriptFailedError(Exception):
    def __init__(self, target_name: str, script_name: str, return_code: int):
        super().__init__(f"Script '{target_name}:{script_name}' failed with return-code {return_code}")
        self.target_name = target_name
        self.script_name = script_name
        self.return_code = return_code
