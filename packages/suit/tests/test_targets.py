import pathlib
from typing import Any, Mapping

import pytest
from suit.targets import ShellScriptSpec, TargetConfig, TargetConfigData


@pytest.mark.parametrize(
    ["raw_data", "expected"],
    [
        ({}, TargetConfigData()),
        (
            {"inherit": ["a", "b", "c"]},
            TargetConfigData(inherit=["a", "b", "c"]),
        ),
        (
            {"scripts": {"format": "black"}},
            TargetConfigData(scripts={"format": ShellScriptSpec("black")}),
        ),
        (
            {"scripts": {"format": {"cmd": "black"}}},
            TargetConfigData(scripts={"format": ShellScriptSpec("black")}),
        ),
        (
            {"scripts": {"format": {"cmd": "black", "args": {"argname": 1}}}},
            TargetConfigData(scripts={"format": ShellScriptSpec("black", {"argname": 1})}),
        ),
    ],
)
def test_build_target(raw_data: Mapping[str, Any], expected: TargetConfigData):
    config = TargetConfig.from_mapping(pathlib.Path("target"), raw_data)
    assert config == TargetConfig(pathlib.Path("target"), expected)
