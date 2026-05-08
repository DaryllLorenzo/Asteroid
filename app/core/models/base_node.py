# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------
from abc import ABC
from abc import abstractmethod


class BaseNode(ABC):
    def __init__(self, x: float = 0, y: float = 0, radius: float = 50) -> None:
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
        self.show_subcanvas = not self.show_subcanvas
        return self.show_subcanvas

    @abstractmethod
    def node_type(self) -> str:
        pass
