# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------

from app.i18n import tr
from app.validation.rule import Rule


class NoEntityInEntitySubcanvas(Rule):
    """Rejects nesting an Actor/Agent inside another entity's subcanvas."""

    def applies_to(self, action_type: str) -> bool:
        return action_type == "subcanvas_add_node"

    def check(self, context: dict) -> str | None:
        if context.get("parent_is_entity") and context.get("child_type") in (
            "actor",
            "agent",
        ):
            return tr(
                "Cannot add an Actor/Agent inside another Actor/Agent's subcanvas."
                " Subcanvases are for Tropos elements"
                " (Goals, Resources, Plans, Softgoals)."
            )
        return None


rule = NoEntityInEntitySubcanvas()
