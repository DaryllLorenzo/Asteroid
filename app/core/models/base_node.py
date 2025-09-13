from abc import ABC, abstractmethod

class BaseNode(ABC):
    def __init__(self, x=0, y=0, radius=50):
        self.x = x
        self.y = y
        self.radius = radius
        self.child_nodes = []
        self.show_subcanvas = False

    def toggle_subcanvas(self):
        """Alterna la visibilidad del subcanvas."""
        self.show_subcanvas = not self.show_subcanvas
        return self.show_subcanvas
    
    @abstractmethod
    def node_type(self) -> str:
        """Cada subclase debe definir qué tipo de nodo es (actor, agent, etc.)."""
        pass