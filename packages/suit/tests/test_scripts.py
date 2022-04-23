import pathlib

import pytest
from suit.collector import SuitConfig, SuitCollector, Target, TargetConfig
from suit.scripts import resolve_scripts, ShellScript


@pytest.mark.skip("not yet")
def test_resolve_scripts():
    target_config = TargetConfig(
        pathlib.Path("root/packages/package-a"),
        {
            "scripts": {"black": "black --check"},
        },
    )
    suit = SuitConfig(pathlib.Path("root/"), {}, [target_config])
    scripts = resolve_scripts(suit, target_config)
    assert scripts is None
