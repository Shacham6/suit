from __future__ import annotations

from suit.collector import Suit, _TargetConfig


class SuitNavigator:
    def __init__(self, suit: Suit):
        self.__suit = suit

    @property
    def targets(self) -> _SuitTargetsNavigator:
        return _SuitTargetsNavigator(self.__suit)


class _SuitTargetsNavigator:
    def __init__(self, suit: Suit):
        self.__suit = suit

    def find(self, pattern):
        return self.__suit.raw_targets

