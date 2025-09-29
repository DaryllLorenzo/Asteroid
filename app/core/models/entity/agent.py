# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------

from app.core.models.base_node import BaseNode

class Agent(BaseNode):
    """Nodo lógico para un Agente."""
    def __init__(self, x=0, y=0, radius=50):
        super().__init__(x, y, radius)

    def node_type(self) -> str:
        return "agent"