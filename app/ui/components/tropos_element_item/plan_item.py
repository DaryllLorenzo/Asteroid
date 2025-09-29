# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------

from app.ui.components.base_tropos_item import BaseTroposItem
from app.core.models.tropos_element.plan import Plan
from PyQt6.QtGui import QBrush, QPen, QColor, QPolygonF
from PyQt6.QtCore import QPointF
import math


class PlanNodeItem(BaseTroposItem):
    def __init__(self, x=0, y=0, radius=50):
        super().__init__(Plan(x, y, radius))

    def _get_distance_to_border(self, pos: QPointF) -> float:
        """Distancia exacta al borde del hexágono."""
        r = self.model.radius
        points = [
            QPointF(-r, 0), QPointF(-r/2, -r/2), QPointF(r/2, -r/2),
            QPointF(r, 0), QPointF(r/2, r/2), QPointF(-r/2, r/2)
        ]
        
        # Calcular distancia mínima a cualquier segmento del hexágono
        min_dist = float('inf')
        n = len(points)
        for i in range(n):
            p1 = points[i]
            p2 = points[(i + 1) % n]
            dist = self._point_to_segment_distance(pos, p1, p2)
            min_dist = min(min_dist, dist)
        return min_dist

    def _point_to_segment_distance(self, p, a, b):
        """Distancia de punto p a segmento ab."""
        ap = QPointF(p.x() - a.x(), p.y() - a.y())
        ab = QPointF(b.x() - a.x(), b.y() - a.y())
        ab2 = ab.x() * ab.x() + ab.y() * ab.y()
        if ab2 == 0:
            return math.sqrt(ap.x() * ap.x() + ap.y() * ap.y())
        t = (ap.x() * ab.x() + ap.y() * ab.y()) / ab2
        t = max(0, min(1, t))
        projection = QPointF(a.x() + t * ab.x(), a.y() + t * ab.y())
        dx = p.x() - projection.x()
        dy = p.y() - projection.y()
        return math.sqrt(dx*dx + dy*dy)

    def _get_new_radius_from_pos(self, pos: QPointF) -> float:
        """Nuevo radio basado en la distancia al centro (aproximación para hexágono)."""
        # Usamos la distancia euclidiana como proxy
        return max((pos.x()**2 + pos.y()**2) ** 0.5, 15.0)

    def paint(self, painter, option, widget=None):
        painter.setBrush(QBrush(QColor(150, 180, 250)))
        painter.setPen(QPen(QColor(0, 0, 0), 2))

        r = self.model.radius
        points = [
            QPointF(-r, 0), QPointF(-r/2, -r/2), QPointF(r/2, -r/2),
            QPointF(r, 0), QPointF(r/2, r/2), QPointF(-r/2, r/2)
        ]
        painter.drawPolygon(QPolygonF(points))