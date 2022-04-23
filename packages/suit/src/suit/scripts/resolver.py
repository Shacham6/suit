from typing import Mapping

from suit.collector import SuitConfig, TargetConfig

from .types import _ScriptBase, CompositeScript, RefScript, ShellScript
from .specs import CompositeScriptSpec, RefScriptSpec, ShellScriptSpec, ScriptSpec


def resolve_scripts(suit: SuitConfig, target_config: TargetConfig) -> Mapping[str, _ScriptBase]:
    """Resolve the scripts by their types."""
    return {
        script_name: _resolve_script(suit, target_config, script_name, script)
        for script_name, script in target_config.data.scripts.items()
    }


__TYPES = {
    ShellScriptSpec: ShellScript,
    RefScriptSpec: RefScript,
    CompositeScriptSpec: CompositeScript,
}


def _resolve_script(
    suit: SuitConfig, target_config: TargetConfig, script_name: str, script_spec: ScriptSpec
) -> _ScriptBase:
    kwargs = {"name": script_name, "specs": script_spec, "suit": suit, "target": target_config}
    for script_spec_cls, script_cls in __TYPES.items():
        if isinstance(script_spec, script_spec_cls):
            return script_cls(**kwargs)
    raise ValueError()
