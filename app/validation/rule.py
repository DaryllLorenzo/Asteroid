# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------

from abc import ABC
from abc import abstractmethod


class Rule(ABC):
    """
    Rule.

    Methods:
        applies_to: Applies To.
        check: Check.
    """

    @abstractmethod
    def applies_to(self, action_type: str) -> bool: ...

    @abstractmethod
    def check(self, context: dict) -> str | None: ...
