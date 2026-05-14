# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------
from abc import ABC
from abc import abstractmethod


class BaseNode(ABC):
    """
    Base Node.

    Methods:
        __init__: Initialize the instance.
        toggle_subcanvas: Toggle Subcanvas.
        node_type: Node Type.
    """

    def __init__(self, x: float = 0, y: float = 0, radius: float = 50) -> None:
        """
        Initialize the instance.

        Args:
            x (float): The x.
            y (float): The y.
            radius (float): The radius.
        """
        self.x: float = x
        self.y: float = y
        self.radius: float = radius
        self.label: str = "Nodo"
        self.color: str = "#3498db"
        self.border_color: str = "#2980b9"
        self.text_color: str = "#ffffff"

        self.text_align: str = "center"
        self.text_width: float = 150
        self.font_size: float = 10

        self.content_offset_x: float = 0.0
        self.content_offset_y: float = 0.0
        self.position_in_subcanvas_x: float = 0.0
        self.position_in_subcanvas_y: float = 0.0

        self.child_nodes: list[object] = []
        self.show_subcanvas: bool = False

    def toggle_subcanvas(self) -> bool:
        """
        Toggle Subcanvas.

        Returns:
            bool: Toggle Subcanvas.
        """
        self.show_subcanvas = not self.show_subcanvas
        return self.show_subcanvas

    @abstractmethod
    def node_type(self) -> str:
        """
        Node Type.

        Returns:
            str: Node Type.
        """
        pass
