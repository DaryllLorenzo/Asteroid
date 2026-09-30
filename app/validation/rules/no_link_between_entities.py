# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------

from app.i18n import tr
from app.validation.rule import Rule

# Display phrase (with article) used in each rule's error message.
_LINK_DESCRIPTIONS: dict[str, str] = {
    "and_decomposition": "an AND Decomposition",
    "or_decomposition": "an OR Decomposition",
    "contribution": "a Contribution",
    "dependency_link": "a Dependency Link",
    "means_end": "a Means-End",
    "why_link": "a Why Link",
}


class NoLinkBetweenEntitiesRule(Rule):
    """Rejects a given arrow_type when both endpoints are Actors/Agents."""

    def __init__(self, arrow_type: str, link_description: str) -> None:
        self._arrow_type = arrow_type
        self._link_description = link_description

    def applies_to(self, action_type: str) -> bool:
        return action_type == "create_edge"

    def check(self, context: dict) -> str | None:
        if (
            context.get("arrow_type") == self._arrow_type
            and context.get("source_is_entity")
            and context.get("dest_is_entity")
        ):
            return tr(
                f"Cannot create {self._link_description} between Actors/Agents."
                " Links are for Tropos elements inside the subcanvas."
            )
        return None


rules = [
    NoLinkBetweenEntitiesRule(arrow_type, description)
    for arrow_type, description in _LINK_DESCRIPTIONS.items()
]
