# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------

from app.core.models.base_node import BaseNode

class HardGoal(BaseNode):
    def __init__(self, x=0, y=0, radius=50):
        super().__init__(x, y, radius)
        self.label = "Hard Goal"
        self.color = "#96c896"      # Verde (equivalente a QColor(150, 200, 150))
        self.border_color = "#000000"
        self.text_color = "#ffffff"

    def node_type(self) -> str:
        return "hard_goal"