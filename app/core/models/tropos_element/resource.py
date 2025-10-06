# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------

from app.core.models.base_node import BaseNode

class Resource(BaseNode):
    def __init__(self, x=0, y=0, radius=50):
        super().__init__(x, y, radius)
        self.label = "Resource"
        self.color = "#c896fa"      # Lila (equivalente a QColor(200, 150, 250))
        self.border_color = "#000000"
        self.text_color = "#ffffff"

    def node_type(self) -> str:
        return "resource"