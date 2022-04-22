import pathlib
from unittest.mock import MagicMock

from suit.collector import Suit, Target
from suit.navigator import SuitNavigator


def test_list_all_targets():
    suit = Suit(
        root=pathlib.Path("root/"),
        local_config={},
        targets=[
            Target(pathlib.Path("root/packages/package-a"), {}),
            Target(pathlib.Path("root/packages/package-b"), {}),
            Target(pathlib.Path("root/tools/tool-a"), {}),
        ],
    )
    navigator = SuitNavigator(suit)
    assert list(navigator.targets.find("*")) == [
        Target(pathlib.Path("root/packages/package-a"), {}),
        Target(pathlib.Path("root/packages/package-b"), {}),
    ]
