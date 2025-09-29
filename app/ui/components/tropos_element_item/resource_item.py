# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------

from app.ui.components.base_tropos_item import BaseTroposItem
from app.core.models.tropos_element.resource import Resource
from PyQt6.QtGui import QBrush, QPen, QColor
from PyQt6.QtCore import QRectF, QPointF
import math


class ResourceNodeItem(BaseTroposItem):
    def __init__(self, x=0, y=0, radius=50):
        super().__init__(Resource(x, y, radius))

    def _get_distance_to_border(self, pos: QPointF) -> float:
        """Distancia exacta al borde del rectángulo."""
        r = self.model.radius
        rect = QRectF(-r, -r/2, 2 * r, r)
        
        # Si el punto está dentro, calcular distancia al borde más cercano
        if rect.contains(pos):
            dist_left = abs(pos.x() - rect.left())
            dist_right = abs(pos.x() - rect.right())
            dist_top = abs(pos.y() - rect.top())
            dist_bottom = abs(pos.y() - rect.bottom())
            return min(dist_left, dist_right, dist_top, dist_bottom)
        else:
            # Si está fuera, calcular distancia al rectángulo
            dx = max(rect.left() - pos.x(), 0, pos.x() - rect.right())
            dy = max(rect.top() - pos.y(), 0, pos.y() - rect.bottom())
            return math.sqrt(dx*dx + dy*dy)

    def _get_new_radius_from_pos(self, pos: QPointF) -> float:
        """Nuevo radio basado en la coordenada X (ancho del rectángulo)."""
        new_r = abs(pos.x())
        return max(new_r, 20.0)

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(painter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(200, 150, 250)))
        painter.setPen(QPen(QColor(0, 0, 0), 2))

        r = self.model.radius
        painter.drawRect(QRectF(-r, -r/2, 2 * r, r))