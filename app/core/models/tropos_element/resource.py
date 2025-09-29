# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------

# app/core/models/tropos_element/resource.py
from app.core.models.base_node import BaseNode

class Resource(BaseNode):
    def __init__(self, x=0, y=0, radius=50):
        super().__init__(x, y, radius)

    def node_type(self) -> str:
        return "resource"
