# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------
from app.ui.components.base_tropos_item import BaseTroposItem
from app.core.models.tropos_element.hard_goal import HardGoal
from PyQt6.QtGui import QBrush, QPen, QColor, QPainterPath, QFont
from PyQt6.QtCore import QRectF, QPointF, Qt
import math

class HardGoalNodeItem(BaseTroposItem):
    def __init__(self, x=0, y=0, radius=60):
        super().__init__(HardGoal(x, y, radius))

    def _get_distance_to_border(self, pos: QPointF) -> float:
        r = self.model.radius
        rect = QRectF(-r, -r/2, 2 * r, r)
        if rect.contains(pos):
            dist_left = abs(pos.x() - rect.left())
            dist_right = abs(pos.x() - rect.right())
            dist_top = abs(pos.y() - rect.top())
            dist_bottom = abs(pos.y() - rect.bottom())
            return min(dist_left, dist_right, dist_top, dist_bottom)
        else:
            dx = max(rect.left() - pos.x(), 0, pos.x() - rect.right())
            dy = max(rect.top() - pos.y(), 0, pos.y() - rect.bottom())
            return math.sqrt(dx*dx + dy*dy)

    def _get_new_radius_from_pos(self, pos: QPointF) -> float:
        new_r = abs(pos.x())
        return max(new_r, 20.0)

    def paint(self, painter, option, widget=None):
        default_color = QColor(150, 200, 150)
        default_border = QColor(0, 0, 0)
        default_text = QColor(255, 255, 255)
        
        fill_color = QColor(self.model.color) if hasattr(self.model, 'color') else default_color
        border_color = QColor(self.model.border_color) if hasattr(self.model, 'border_color') else default_border
        text_color = QColor(self.model.text_color) if hasattr(self.model, 'text_color') else default_text
        
        painter.setRenderHint(painter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(fill_color))
        painter.setPen(QPen(border_color, 2))

        r = self.model.radius
        rect = QRectF(-r, -r/2, 2 * r, r)
        path = QPainterPath()
        path.addRoundedRect(rect, r/2, r/2)
        painter.drawPath(path)

        #   DIBUJAR TEXTO MULTILÍNEA
        self.draw_multiline_text(painter, text_color)

        if self.isSelected():
            painter.setPen(QPen(Qt.GlobalColor.yellow, 3))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(path)

    def get_serializable_properties(self):
        base_properties = super().get_serializable_properties()
        base_properties['node_type'] = 'hard_goal'
        return base_properties

    def update_properties(self, properties: dict):
        super().update_properties(properties)