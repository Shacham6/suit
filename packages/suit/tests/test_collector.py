import io
from typing import Any, Mapping
from unittest.mock import MagicMock

import pytest
import toml
from suit.collector import Target, TargetsCollector, _pyproject_uses_suit


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
    collector = TargetsCollector(root)
    results = list(collector.collect())
    assert results == [Target(root=root, target=suit_project_file, suit={})]


def test_is_pyproject_uses_suit():
    assert _pyproject_uses_suit({"tool": {"suit": {}}})
    assert not _pyproject_uses_suit({})
