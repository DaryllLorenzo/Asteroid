# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------

from app.validation.rule import Rule
from app.validation.rules.no_entity_in_entity_subcanvas import (
    rule as no_entity_in_entity_subcanvas,
)
from app.validation.rules.no_link_between_entities import (
    rules as no_link_between_entities_rules,
)


class Validator:
    """Runs the active Rule set against a canvas action's context."""

    def __init__(self) -> None:
        self.active: bool = False
        self._rules: list[Rule] = [
            no_entity_in_entity_subcanvas,
            *no_link_between_entities_rules,
        ]

    def validate(self, action_type: str, context: dict) -> list[str]:
        if not self.active:
            return []
        errors: list[str] = []
        for rule in self._rules:
            if rule.applies_to(action_type):
                error = rule.check(context)
                if error:
                    errors.append(error)
        return errors
