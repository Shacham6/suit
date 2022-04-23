from typing import Mapping

from suit.collector import SuitConfig, TargetConfig

from .types import _ScriptBase


def resolve_scripts(suit: SuitConfig, target_config: TargetConfig) -> Mapping[str, _ScriptBase]:
    """Resolve the scripts by their types."""
    return {}
