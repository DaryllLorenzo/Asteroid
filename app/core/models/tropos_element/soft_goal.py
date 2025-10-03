# soft_goal.py
# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------

from app.core.models.base_node import BaseNode

class SoftGoal(BaseNode):
    def __init__(self, x=0, y=0, radius=50):
        super().__init__(x, y, radius)
        self.label = "Soft Goal"
        self.color = "#dcdcb4"      # Beige (equivalente a QColor(220, 220, 180))
        self.border_color = "#000000"
        self.text_color = "#000000"  # Texto negro para mejor contraste con fondo claro

    def node_type(self) -> str:
        return "soft_goal"