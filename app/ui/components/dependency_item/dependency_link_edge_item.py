# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------

# app/ui/components/dependency_item/dependency_link_edge_item.py
from PyQt6.QtGui import QPainter, QBrush, QColor, QPolygonF
from PyQt6.QtCore import QPointF
import math

from app.ui.components.base_edge_item import BaseEdgeItem

class DependencyLinkArrowItem(BaseEdgeItem):
    """Flecha tipo dependency: línea de centro a centro con triángulo en el medio."""

    def __init__(self, source_node, dest_node):
        super().__init__(source_node, dest_node, color=QColor(0, 0, 0), dashed=False)

    def boundingRect(self):
        """Extiende el bounding rect para incluir el triángulo en medio de la línea."""
        extra = 15  # suficiente para el triángulo
        return super().boundingRect().adjusted(-extra, -extra, extra, extra)

    def paint(self, painter: QPainter, option, widget=None):
        if not self.source_node or not self.dest_node:
            return

        # Actualizar posición de la línea
        self.update_position()
        line = self.line()
        if line.length() == 0:
            return

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(self.pen())
        painter.drawLine(line)

        # Triángulo en el punto medio de la línea
        mid_x = (line.x1() + line.x2()) / 2
        mid_y = (line.y1() + line.y2()) / 2
        p_tip = QPointF(mid_x, mid_y)

        # Ángulo de la línea
        angle = math.atan2(line.dy(), line.dx())
        size = 12.0
        p1 = QPointF(p_tip.x() - size * math.cos(angle - math.pi/6),
                     p_tip.y() - size * math.sin(angle - math.pi/6))
        p2 = QPointF(p_tip.x() - size * math.cos(angle + math.pi/6),
                     p_tip.y() - size * math.sin(angle + math.pi/6))

        poly = QPolygonF([p_tip, p1, p2])
        painter.setBrush(QBrush(self.pen().color()))
        painter.drawPolygon(poly)
