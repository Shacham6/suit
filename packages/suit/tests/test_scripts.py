import io
import pathlib
from typing import Any, Iterable, List, Mapping, cast
from unittest.mock import MagicMock
from mockitup import allow

import pytest
import toml
from box import Box
from suit.collector import (
    RootDirectoryNotFound,
    Suit,
    SuitCollector,
    Target,
    TargetScript,
    _find_root_configuration,
    _pyproject_uses_suit,
    _TargetConfig,
)


def test_target_script_compiled():
    suit = Suit(
        root=pathlib.Path("root/"),
        project_config={},
        raw_targets=[
            _TargetConfig(
                pathlib.Path("root/packages/package-a"),
                {"target": {"scripts": {"format": "black --config {root.path} {local.path}"}}},
            )
        ],
    )
    package_a_target = suit.targets["packages/package-a"]
    assert package_a_target.scripts == {
        "format": TargetScript(
            "black --config {root.path} {local.path}",
            root=Box(path=pathlib.Path("root/")),
            local=Box(path=pathlib.Path("root/packages/package-a")),
            args=Box(),
        )
    }


def test_compile_target_script():
    target_config = _TargetConfig(
        pathlib.Path("root/packages/package-a"),
        {"target": {"scripts": {"format": "black --config {root.path} {local.path}"}}},
    )
    suit = Suit(root=pathlib.Path("root/"), project_config={}, raw_targets=[target_config])

    result = TargetScript.compile_inline("black --config {root.path} {local.path}", suit, target_config)

    assert result == TargetScript(
        cmd="black --config {root.path} {local.path}",
        root=Box(path=pathlib.Path("root/")),
        local=Box(path=pathlib.Path("root/packages/package-a")),
        args=Box(),
    )


def test_execute_script():
    target_script = TargetScript("echo 'lol {root.path}'", Box(path=pathlib.Path("root/")), Box(), Box())
    script_execution = target_script.execute()
    assert cast(bytes, script_execution.stdout.read()).decode("utf-8") == "lol root\n"


def test_script_inheritance():
    target_config = _TargetConfig(
        pathlib.Path("root/packages/package-a"),
        {
            "target": {
                "inherit": ["helloer"],
            }
        },
    )
    project_config = {
        "templates": {
            "helloer": {
                "scripts": {
                    "hello": "echo I'm a helloer from {local.path}",
                }
            }
        }
    }
    suit = Suit(pathlib.Path("root/"), project_config, [target_config])

    assert suit.targets["packages/package-a"].scripts == {
        "hello": TargetScript(
            "echo I'm a helloer from {local.path}",
            Box(path=pathlib.Path("root/")),
            Box(path=pathlib.Path("root/packages/package-a")),
            Box(),
        )
    }


def test_args_are_passed_in_target():
    target_config = _TargetConfig(
        pathlib.Path("root/packages/package-a"),
        {
            "target": {
                "inherit": ["helloer"],
                "args": {"what_im_here_to_say": "praise the sun!!"},
            }
        },
    )
    project_config = {
        "templates": {
            "helloer": {
                "scripts": {
                    "hello": "echo I'm a helloer from {local.path}, and I'm here to say '{args.what_im_here_to_say}'"
                }
            }
        }
    }
    suit = Suit(pathlib.Path("root/"), project_config, [target_config])

    assert suit.targets["packages/package-a"].scripts == {
        "hello": TargetScript(
            "echo I'm a helloer from {local.path}, and I'm here to say '{args.what_im_here_to_say}'",
            Box(path=pathlib.Path("root/")),
            Box(path=pathlib.Path("root/packages/package-a")),
            Box(what_im_here_to_say="praise the sun!!"),
        )
    }
