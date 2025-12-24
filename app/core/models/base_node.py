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
        self.label = "Nodo"  # label personalizable
        self.color = "#3498db"  # color personalizable (azul por defecto)
        self.border_color = "#2980b9"  # color del borde
        self.text_color = "#ffffff"  # color del texto
        
        # Offset del contenido (texto/icono) relativo al centro
        self.content_offset_x = 0.0 
        self.content_offset_y = 0.0

        # Posición del nodo dentro de su behaviour canvas (subcanvas)
        self.position_in_subcanvas_x = 0.0
        self.position_in_subcanvas_y = 0.0

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