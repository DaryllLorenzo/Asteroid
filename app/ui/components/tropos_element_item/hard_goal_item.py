# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------

from app.ui.components.base_tropos_item import BaseTroposItem
from app.core.models.tropos_element.hard_goal import HardGoal
from PyQt6.QtGui import QBrush, QPen, QColor, QPainterPath
from PyQt6.QtCore import QRectF, QPointF
import math


class HardGoalNodeItem(BaseTroposItem):
    def __init__(self, x=0, y=0, radius=60):
        super().__init__(HardGoal(x, y, radius))

    def _get_distance_to_border(self, pos: QPointF) -> float:
        """Distancia exacta al borde de la píldora."""
        r = self.model.radius
        rect = QRectF(-r, -r/2, 2 * r, r)
        
        # Si el punto está dentro del rectángulo, calcular distancia al borde más cercano
        if rect.contains(pos):
            # Distancia a los bordes horizontal y vertical
            dist_left = abs(pos.x() - rect.left())
            dist_right = abs(pos.x() - rect.right())
            dist_top = abs(pos.y() - rect.top())
            dist_bottom = abs(pos.y() - rect.bottom())
            return min(dist_left, dist_right, dist_top, dist_bottom)
        else:
            # Si está fuera, calcular distancia al rectángulo redondeado
            # Simplificación: usar distancia al rectángulo principal
            dx = max(rect.left() - pos.x(), 0, pos.x() - rect.right())
            dy = max(rect.top() - pos.y(), 0, pos.y() - rect.bottom())
            return math.sqrt(dx*dx + dy*dy)

    def _get_new_radius_from_pos(self, pos: QPointF) -> float:
        """Calcula nuevo 'radio' basado en la distancia horizontal (ancho de la píldora)."""
        # La píldora tiene ancho = 2 * r, así que r = ancho / 2
        # Usamos la coordenada X como principal (porque es horizontal)
        new_r = abs(pos.x())
        return max(new_r, 20.0)  # mínimo r=20

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(painter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(150, 200, 150)))
        painter.setPen(QPen(QColor(0, 0, 0), 2))

        r = self.model.radius
        rect = QRectF(-r, -r/2, 2 * r, r)
        path = QPainterPath()
        path.addRoundedRect(rect, r/2, r/2)
        painter.drawPath(path)