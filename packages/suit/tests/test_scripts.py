import pathlib
from typing import Mapping

import pytest
from suit.collector import SuitConfig
from suit.scripts import ShellScript, resolve_scripts
from suit.scripts.types import CompositeScript
from suit.targets import CompositeScriptSpec, RefScriptSpec, ShellScriptSpec, TargetConfig, TargetConfigData


def test_resolve_scripts():
    target_config = TargetConfig(
        pathlib.Path("root/target"),
        TargetConfigData(
            scripts={
                "black": ShellScriptSpec("black"),
                "lint": CompositeScriptSpec(
                    [
                        RefScriptSpec("black"),
                        ShellScriptSpec("pylint"),
                    ]
                ),
            }
        ),
    )
    suit_config = SuitConfig(pathlib.Path("root/"), {}, [target_config])
    scripts = resolve_scripts(suit_config, target_config)
    assert scripts == {
        "black": ShellScript(
            name="black",
            specs=ShellScriptSpec("black"),
            suit=suit_config,
            target=target_config,
        ),
        "lint": CompositeScript(
            name="lint",
            specs=CompositeScriptSpec(
                [
                    RefScriptSpec("black"),
                    ShellScriptSpec("pylint"),
                ]
            ),
            suit=suit_config,
            target=target_config,
        ),
    }
