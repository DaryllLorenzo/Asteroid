# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------

# app/ui/components/dependency_item/or_decomposition_edge_item.py
from PyQt6.QtGui import QPainter, QPen, QPolygonF
from PyQt6.QtCore import QPointF, Qt
import math

from app.ui.components.base_edge_item import BaseEdgeItem

class OrDecompositionArrowItem(BaseEdgeItem):
    """Cabeza triangular sin relleno en la punta (OR)."""

    def __init__(self, source_node, dest_node):
        super().__init__(source_node, dest_node, color=QPen().color(), dashed=False)

    def paint(self, painter: QPainter, option, widget=None):
        if not self.source_node or not self.dest_node:
            return

        self.update_position()
        line = self.line()
        if line.length() == 0:
            return

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(self.pen())

        # Tamaño de la cabeza de flecha
        size = 12.0

        # Calcular ángulo de la línea
        angle = math.atan2(line.dy(), line.dx())

        # Ajustar la línea para que termine antes de la punta
        p_start = line.p1()
        p_tip = line.p2()
        p_line_end = QPointF(p_tip.x() - size * math.cos(angle),
                             p_tip.y() - size * math.sin(angle))
        painter.drawLine(p_start, p_line_end)

        # Calcular triángulo sin relleno
        p_base = p_line_end
        perp_x = math.sin(angle) * (size * 0.5)
        perp_y = -math.cos(angle) * (size * 0.5)
        p1 = QPointF(p_base.x() + perp_x, p_base.y() + perp_y)
        p2 = QPointF(p_base.x() - perp_x, p_base.y() - perp_y)

        poly = QPolygonF([p_tip, p1, p2])
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPolygon(poly)

