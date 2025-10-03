# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------

from abc import ABC, abstractmethod

class BaseNode(ABC):
    def __init__(self, x=0, y=0, radius=50):
        self.x = x
        self.y = y
        self.radius = radius
        self.label = "Nodo"  # ✅ Nuevo: label personalizable
        self.color = "#3498db"  # ✅ Nuevo: color personalizable (azul por defecto)
        self.border_color = "#2980b9"  # ✅ Nuevo: color del borde
        self.text_color = "#ffffff"  # ✅ Nuevo: color del texto
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