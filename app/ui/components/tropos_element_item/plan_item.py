# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------

from app.ui.components.base_tropos_item import BaseTroposItem
from app.core.models.tropos_element.plan import Plan
from PyQt6.QtGui import QBrush, QPen, QColor, QPolygonF, QFont
from PyQt6.QtCore import QPointF, Qt, QRectF
import math

class PlanNodeItem(BaseTroposItem):
    def __init__(self, x=0, y=0, radius=50):
        super().__init__(Plan(x, y, radius))

    def _get_distance_to_border(self, pos: QPointF) -> float:
        r = self.model.radius
        points = [
            QPointF(-r, 0), QPointF(-r/2, -r/2), QPointF(r/2, -r/2),
            QPointF(r, 0), QPointF(r/2, r/2), QPointF(-r/2, r/2)
        ]
        min_dist = float('inf')
        n = len(points)
        for i in range(n):
            p1 = points[i]
            p2 = points[(i + 1) % n]
            dist = self._point_to_segment_distance(pos, p1, p2)
            min_dist = min(min_dist, dist)
        return min_dist

    def _point_to_segment_distance(self, p, a, b):
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
        return max((pos.x()**2 + pos.y()**2) ** 0.5, 15.0)

    def paint(self, painter, option, widget=None):
        default_color = QColor(150, 180, 250)
        default_border = QColor(0, 0, 0)
        default_text = QColor(255, 255, 255)
        
        fill_color = QColor(self.model.color) if hasattr(self.model, 'color') else default_color
        border_color = QColor(self.model.border_color) if hasattr(self.model, 'border_color') else default_border
        text_color = QColor(self.model.text_color) if hasattr(self.model, 'text_color') else default_text
        
        painter.setBrush(QBrush(fill_color))
        painter.setPen(QPen(border_color, 2))

        r = self.model.radius
        points = [
            QPointF(-r, 0), QPointF(-r/2, -r/2), QPointF(r/2, -r/2),
            QPointF(r, 0), QPointF(r/2, r/2), QPointF(-r/2, r/2)
        ]
        painter.drawPolygon(QPolygonF(points))

        #   DIBUJAR TEXTO MULTILÍNEA
        self.draw_multiline_text(painter, text_color)

        if self.isSelected():
            painter.setPen(QPen(Qt.GlobalColor.yellow, 3))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPolygon(QPolygonF(points))

    def get_serializable_properties(self):
        base_properties = super().get_serializable_properties()
        base_properties['node_type'] = 'plan'
        return base_properties
    
    def update_properties(self, properties: dict):
        super().update_properties(properties)