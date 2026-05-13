from abc import ABC
from abc import abstractmethod


class Rule(ABC):
    @abstractmethod
    def applies_to(self, action_type: str) -> bool: ...

    @abstractmethod
    def check(self, context: dict) -> str | None: ...
