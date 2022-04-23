from typing import Mapping

from suit.collector import SuitConfig, TargetConfig

from .specs import CompositeScriptSpec, RefScriptSpec, ScriptSpec, ShellScriptSpec
from .types import CompositeScript, RefScript, ShellScript, _ScriptBase


def resolve_scripts(suit: SuitConfig, target_config: TargetConfig) -> Mapping[str, _ScriptBase]:
    """Resolve the scripts by their types."""
    target_scripts = {}

    for inheritance_name in target_config.data.inherit:
        for script_name, inherited_script in suit.project_config.templates[inheritance_name].scripts.items():
            target_scripts[script_name] = resolve_script(suit, target_config, script_name, inherited_script)

    for script_name, inline_script in target_config.data.scripts.items():
        target_scripts[script_name] = resolve_script(suit, target_config, script_name, inline_script)

    return target_scripts


__TYPES = {
    ShellScriptSpec: ShellScript,
    RefScriptSpec: RefScript,
    CompositeScriptSpec: CompositeScript,
}


def resolve_script(
    suit: SuitConfig, target_config: TargetConfig, script_name: str, script_spec: ScriptSpec
) -> _ScriptBase:
    kwargs = {"name": script_name, "specs": script_spec, "suit": suit, "target": target_config}
    for script_spec_cls, script_cls in __TYPES.items():
        if isinstance(script_spec, script_spec_cls):
            return script_cls(**kwargs)
    raise ValueError()
