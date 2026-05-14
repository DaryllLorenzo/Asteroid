# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------

from app.validation.rule import Rule


class NoOrDecompositionBetweenEntities(Rule):
    """
    No Or Decomposition Between Entities.

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
            context.get("arrow_type") == "or_decomposition"
            and context.get("source_is_entity")
            and context.get("dest_is_entity")
        ):
            return (
                "No se puede crear un enlace OR Decomposition entre "
                "Actores/Agentes. Los enlaces son para elementos Tropos "
                "dentro del subcanvas."
            )
        return None


rule = NoOrDecompositionBetweenEntities()
