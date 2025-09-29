# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------

# app/ui/components/dependency_item/contribution_edge_item.py
from PyQt6.QtGui import QPainter, QFont, QPen
from PyQt6.QtCore import QPointF
import math
from app.ui.components.base_edge_item import BaseEdgeItem

class ContributionArrowItem(BaseEdgeItem):
    """Flecha abierta tipo V y símbolo '+' cerca del cuerpo."""

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
        painter.drawLine(line)

        angle = math.atan2(line.dy(), line.dx())
        ux = math.cos(angle)
        uy = math.sin(angle)
        perp_x = -uy
        perp_y = ux

        end = line.p2()
        size = 12.0

        # V abierta
        pA = QPointF(end.x() - ux * size + perp_x * (size * 0.4),
                     end.y() - uy * size + perp_y * (size * 0.4))
        pB = QPointF(end.x() - ux * size - perp_x * (size * 0.4),
                     end.y() - uy * size - perp_y * (size * 0.4))
        painter.drawLine(end, pA)
        painter.drawLine(end, pB)

        # símbolo '+' cerca del cuerpo
        pos = line.pointAt(0.6)
        painter.save()
        painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        painter.drawText(pos, "+")
        painter.restore()
