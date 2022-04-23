import pathlib
from typing import Mapping

import pytest
from suit.collector import SuitConfig
from suit.scripts import ShellScript, resolve_scripts
from suit.targets import ShellScriptSpec, TargetConfig, TargetConfigData


def test_resolve_scripts():
    target_config = TargetConfig(
        pathlib.Path("root/target"),
        TargetConfigData(
            scripts={
                "format": ShellScriptSpec("black"),
            }
        ),
    )
    suit_config = SuitConfig(pathlib.Path("root/"), {}, [target_config])
    scripts = resolve_scripts(suit_config, target_config)
    assert scripts == {
        "format": ShellScript(
            name="format",
            specs=ShellScriptSpec("black"),
            suit=suit_config,
            target=target_config,
        )
    }
