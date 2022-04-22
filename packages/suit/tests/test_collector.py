import io
import pathlib
import string
from typing import Any, Iterable, List, Mapping, cast
from unittest.mock import MagicMock

import pytest
import toml
from box import Box
from suit.collector import (
    RootDirectoryNotFound,
    Suit,
    SuitCollector,
    Target,
    Targets,
    TargetScript,
    _find_root_configuration,
    _pyproject_uses_suit,
    _TargetConfig,
)


def pyproject_toml_file_mock(*, path: str, content: Mapping[str, Any]) -> MagicMock:
    mock = MagicMock()
    mock.is_file.return_value = True
    mock.exists.return_value = True

    parent_mock = MagicMock()
    parent_mock.__str__.return_value = path

    mock.parent = parent_mock
    mock.__str__.return_value = f"{path.strip('/')}/pyproject.toml"

    mock.open.return_value = io.BytesIO(toml.dumps(content).encode("utf-8"))
    return mock


def test_find_pyproject_toml_with_suit_configured():
    root = MagicMock()

    suit_project_file = pyproject_toml_file_mock(
        path="packages/suit", content={"tool": {"suit": {}}}
    )

    root.glob.return_value = (
        suit_project_file,
        pyproject_toml_file_mock(path="packages/notsuit", content={}),
    )
    collector = SuitCollector(root, {})
    results = collector.collect()
    assert results.root == root
    assert results.raw_targets == [
        _TargetConfig(path=suit_project_file.parent, data={})
    ]


def test_is_pyproject_uses_suit():
    assert _pyproject_uses_suit({"tool": {"suit": {}}})
    assert not _pyproject_uses_suit({})


def test_find_root_directory_of_project():
    starting_file = MagicMock()
    starting_file.is_file.return_value = True

    starting_file_path = MagicMock()

    starting_file.parent = starting_file_path

    root = MagicMock()
    root.joinpath.exists = True

    starting_file_path.parents = [MagicMock(), MagicMock(), root, MagicMock()]

    _find_root_configuration(starting_file)


def test_find_root_directory_of_project_raises_when_not_found():
    starting_path = MagicMock()
    starting_path.is_file.return_value = False

    a, b, c = MagicMock(), MagicMock(), MagicMock()

    for mock in (starting_path, a, b, c):
        mock.joinpath.return_value = MagicMock(exists=MagicMock(return_value=False))

    starting_path.parents = a, b, c

    with pytest.raises(RootDirectoryNotFound) as result:
        _find_root_configuration(starting_path)
    assert result.value.searched_paths == [starting_path, a, b, c]


def test_targets_calculation_relative_to_root():
    suit = Suit(
        root=pathlib.Path("root/"),
        project_config={},
        raw_targets=[
            _TargetConfig(pathlib.Path("root/packages/package-a"), {}),
            _TargetConfig(pathlib.Path("root/packages/package-b"), {}),
        ],
    )
    assert list(suit.targets.keys()) == [
        "packages/package-a",
        "packages/package-b",
    ]


def __targets_to_names(targets: Iterable[Target]) -> List[str]:
    return [target.name for target in targets]


def test_filter_targets():
    suit = Suit(
        root=pathlib.Path("root/"),
        project_config={},
        raw_targets=[
            _TargetConfig(pathlib.Path("root/packages/package-a"), {}),
            _TargetConfig(pathlib.Path("root/packages/package-b"), {}),
            _TargetConfig(pathlib.Path("root/tools/tool-a"), {}),
        ],
    )
    assert __targets_to_names(suit.targets.find("packages")) == [
        "packages/package-a",
        "packages/package-b",
    ]
    assert __targets_to_names(suit.targets.find("tools")) == [
        "tools/tool-a",
    ]

    assert __targets_to_names(suit.targets.find("packages/package-a")) == [
        "packages/package-a",
    ]


def test_target_script_compiled():
    suit = Suit(
        root=pathlib.Path("root/"),
        project_config={},
        raw_targets=[
            _TargetConfig(
                pathlib.Path("root/packages/package-a"),
                {
                    "target": {
                        "scripts": {"format": "black --config {root.path} {local.path}"}
                    }
                },
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
    suit = Suit(
        root=pathlib.Path("root/"), project_config={}, raw_targets=[target_config]
    )

    result = TargetScript.compile_inline(
        "black --config {root.path} {local.path}", suit, target_config
    )

    assert result == TargetScript(
        cmd="black --config {root.path} {local.path}",
        root=Box(path=pathlib.Path("root/")),
        local=Box(path=pathlib.Path("root/packages/package-a")),
        args=Box(),
    )


def test_execute_script():
    target_script = TargetScript(
        "echo 'lol {root.path}'", Box(path=pathlib.Path("root/")), Box(), Box()
    )
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
            "echo I'm a helloer from {local.path}",
            Box(path=pathlib.Path("root/")),
            Box(path=pathlib.Path("root/packages/package-a")),
            Box(what_im_here_to_say="praise the sun!!"),
        )
    }
