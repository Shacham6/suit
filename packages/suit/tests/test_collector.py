import io
from typing import Any, Mapping
from unittest.mock import MagicMock

import pytest
import toml
from suit.collector import (
    RootDirectoryNotFound,
    SuitCollector,
    _TargetConfig,
    _find_root_configuration,
    _pyproject_uses_suit,
)


def pyproject_toml_file_mock(*, path: str, content: Mapping[str, Any]) -> MagicMock:
    mock = MagicMock()

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
    assert results.targets == [_TargetConfig(path=suit_project_file, data={})]


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
