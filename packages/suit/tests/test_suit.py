import pathlib

from suit.collector import SuitConfig
from suit.targets import TargetConfig, TargetConfigData


def test_targets_sorted_relatively_to_root():
    target_config = TargetConfig(pathlib.Path("root/packages/package-a"), TargetConfigData())
    suit_config = SuitConfig(pathlib.Path("root/"), {}, [target_config])
    assert suit_config.targets == {"packages/package-a": target_config}
