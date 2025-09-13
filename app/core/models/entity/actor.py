from app.core.models.base_node import BaseNode

class Actor(BaseNode):
    """Nodo lógico para un Actor."""
    def __init__(self, x=0, y=0, radius=50):
        super().__init__(x, y, radius)

    def node_type(self) -> str:
        return "actor"