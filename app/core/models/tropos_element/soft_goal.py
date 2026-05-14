# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------

from app.core.models.base_node import BaseNode


class SoftGoal(BaseNode):
    """
    Soft Goal.

    Methods:
        __init__: Initialize the instance.
        node_type: Node Type.
    """

    def __init__(self, x=0, y=0, radius=50):
        """
        Initialize the instance.

        Args:
            x: The x.
            y: The y.
            radius: The radius.
        """
        super().__init__(x, y, radius)
        self.label = "Soft Goal"
        self.color = "#dcdcb4"  # Beige (equivalente a QColor(220, 220, 180))
        self.border_color = "#000000"
        self.text_color = "#000000"  # Text negro for mejor contraste with fondo claro

    def node_type(self) -> str:
        """
        Node Type.

        Returns:
            str: Node Type.
        """
        return "soft_goal"
