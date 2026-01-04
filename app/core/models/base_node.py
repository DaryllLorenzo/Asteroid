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
        self.label = "Nodo"
        self.color = "#3498db"
        self.border_color = "#2980b9"
        self.text_color = "#ffffff"
        
        self.text_align = "center"  
        self.text_width = 150
        self.font_size = 10 

        self.content_offset_x = 0.0 
        self.content_offset_y = 0.0
        self.position_in_subcanvas_x = 0.0
        self.position_in_subcanvas_y = 0.0

        self.child_nodes = []
        self.show_subcanvas = False

    def toggle_subcanvas(self):
        self.show_subcanvas = not self.show_subcanvas
        return self.show_subcanvas
    
    @abstractmethod
    def node_type(self) -> str:
        pass