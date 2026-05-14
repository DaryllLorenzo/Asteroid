# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------

from app.core.models.base_node import BaseNode


class Resource(BaseNode):
    """
    Resource.

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
        self.label = "Resource"
        self.color = "#c896fa"  # Lila (equivalente a QColor(200, 150, 250))
        self.border_color = "#000000"
        self.text_color = "#ffffff"

    def node_type(self) -> str:
        """
        Node Type.

        Returns:
            str: Node Type.
        """
        return "resource"
