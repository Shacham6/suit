from typing import Any, Iterable, NamedTuple, Tuple

from rich.text import Text

from ..console import console


class ExecutionPlanStage(NamedTuple):
    target: str
    script_name: str
    script: Any


class TargetScriptExecutor:
    def __init__(self, execution_plan: Iterable[ExecutionPlanStage]):
        self.__execution_plan = execution_plan

    def execute(self, is_dry_run: bool = False):
        for target_name, target_script_name, target_script in self.__execution_plan:
            console.log(
                Text.assemble(
                    "Will run '",
                    Text.assemble(target_name, ":", target_script_name, style="yellow italic"),
                    "'...",
                )
            )
            if is_dry_run:
                continue
            result = target_script.execute()
            return_code = result.wait()
            for out_line_bytes in result.stdout:
                out_line = out_line_bytes.decode("utf-8")
                out_text = Text.assemble(
                    ("OUT | ", "bold"),
                    out_line.rstrip("\n"),
                )
                out_text.pad_left(4)
                console.log(out_text)

            for err_line_bytes in result.stderr:
                err_line = err_line_bytes.decode("utf-8")
                err_text = Text.assemble(
                    ("ERR | ", "red bold"),
                    err_line.rstrip("\n"),
                )
                err_text.pad_left(4)
                console.log(err_text)

            if return_code != 0:
                console.log(f"[red]Target script exited with return-code [bold]{return_code}[/][/]")
                raise ScriptFailedError(target_name, target_script_name, return_code)


class ScriptFailedError(Exception):
    def __init__(self, target_name: str, script_name: str, return_code: int):
        super().__init__(f"Script '{target_name}:{script_name}' failed with return-code {return_code}")
        self.target_name = target_name
        self.script_name = script_name
        self.return_code = return_code
