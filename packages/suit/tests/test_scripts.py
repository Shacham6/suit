import pathlib
from typing import Mapping

import pytest
from suit.collector import SuitConfig
from suit.config import ProjectConfig, SuitTemplate
from suit.scripts.resolver import ShellScript, resolve_scripts
from suit.scripts.types import CompositeScript, CompositeScriptSpec, RefScriptSpec, ShellScriptSpec
from suit.targets import TargetConfig, TargetConfigData


def test_resolve_scripts_converts_to_final_objects():
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
    suit_config = SuitConfig(pathlib.Path("root/"), ProjectConfig(), [target_config])
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


def test_resolve_performs_inheritance_of_targets():
    target_config = TargetConfig(pathlib.Path("root/package"), TargetConfigData(inherit=["package"]))
    suit_config = SuitConfig(
        pathlib.Path("root/"),
        ProjectConfig(templates={"package": SuitTemplate(scripts={"lint": ShellScriptSpec("pylint")})}),
        [target_config],
    )
    scripts = resolve_scripts(suit_config, target_config)
    assert "lint" in scripts
