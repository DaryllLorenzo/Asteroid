# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------

from app.core.models.base_node import BaseNode


class HardGoal(BaseNode):
    """
    Hard Goal.

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
        self.label = "Hard Goal"
        self.color = "#96c896"  # Verde (equivalente a QColor(150, 200, 150))
        self.border_color = "#000000"
        self.text_color = "#ffffff"

    def node_type(self) -> str:
        """
        Node Type.

        Returns:
            str: Node Type.
        """
        return "hard_goal"
