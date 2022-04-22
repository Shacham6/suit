from typing import Any, Mapping
from unittest.mock import MagicMock
import pytest

import toml
from suit.collector import TargetsCollector, _pyproject_uses_suit, Target


def pyproject_toml_file_mock(*, path: str, content: Mapping[str, Any]) -> MagicMock:
    mock = MagicMock()

    parent_mock = MagicMock()
    parent_mock.__str__.return_value = path

    mock.parent = parent_mock
    mock.__str__.return_value = f"{path.strip('/')}/pyproject.toml"
    mock.read_text.return_value = toml.dumps(content)
    return mock


def test_find_pyproject_toml_with_suit_configured():
    root = MagicMock()
    root.glob.return_value = (
        pyproject_toml_file_mock(path="packages/suit", content={"tool": {"suit": {}}}),
        pyproject_toml_file_mock(path="packages/notsuit", content={}),
    )
    collector = TargetsCollector(root)
    results = list(collector.collect())
    assert results == [
        Target()
    ]


def test_is_pyproject_uses_suit():
    assert _pyproject_uses_suit({"tool": {"suit": {}}})
    assert not _pyproject_uses_suit({})
