# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------

from app.i18n import tr
from app.validation.rule import Rule


class NoMeansEndBetweenEntities(Rule):
    """
    No Means End Between Entities.

    Methods:
        applies_to: Applies To.
        check: Check.
    """

    def applies_to(self, action_type: str) -> bool:
        """
        Applies To.

        Args:
            action_type (str): The action type.

        Returns:
            bool: Applies To.
        """
        return action_type == "create_edge"

    def check(self, context: dict) -> str | None:
        """
        Check.

        Args:
            context (dict): The context.

        Returns:
            str | None: Check.
        """
        if (
            context.get("arrow_type") == "means_end"
            and context.get("source_is_entity")
            and context.get("dest_is_entity")
        ):
            return tr(
                "Cannot create a Means-End between Actors/Agents. Links are for Tropos elements inside the subcanvas."
            )
        return None


rule = NoMeansEndBetweenEntities()
