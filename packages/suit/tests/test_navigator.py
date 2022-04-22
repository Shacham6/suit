import pathlib
from unittest.mock import MagicMock

from suit.collector import Suit, _TargetConfig
from suit.navigator import SuitNavigator


def test_list_all_targets():
    suit = Suit(
        root=pathlib.Path("root/"),
        local_config={},
        raw_targets=[
            _TargetConfig(pathlib.Path("root/packages/package-a"), {}),
            _TargetConfig(pathlib.Path("root/packages/package-b"), {}),
            _TargetConfig(pathlib.Path("root/tools/tool-a"), {}),
        ],
    )
    navigator = SuitNavigator(suit)
    assert list(navigator.targets.find("*")) == [
        _TargetConfig(pathlib.Path("root/packages/package-a"), {}),
        _TargetConfig(pathlib.Path("root/packages/package-b"), {}),
    ]
