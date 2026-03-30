# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------

# app/ui/components/dependency_item/contribution_edge_item.py
from PyQt6.QtGui import QPainter, QFont, QPen, QBrush, QPolygonF
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

        # NO llamar a update_position() aquí para evitar temblor
        path = self.path()
        if path.isEmpty():
            return

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(self.pen())

        # Dibujar la ruta (línea con control points si existen)
        painter.drawPath(path)

        # Obtener punto final y dirección para la punta de flecha
        end_point = self._end_point
        start_point = self._start_point

        # Determinar el último segmento para dibujar la punta
        if self.control_points:
            last_point = self.control_points[-1]
        else:
            last_point = self._start_point

        # Calcular ángulo del último segmento
        dx = end_point.x() - last_point.x()
        dy = end_point.y() - last_point.y()

        if dx == 0 and dy == 0:
            return

        angle = math.atan2(dy, dx)
        ux = math.cos(angle)
        uy = math.sin(angle)
        perp_x = -uy
        perp_y = ux

        size = 12.0

        # V abierta (punta de flecha)
        pA = QPointF(end_point.x() - ux * size + perp_x * (size * 0.4),
                     end_point.y() - uy * size + perp_y * (size * 0.4))
        pB = QPointF(end_point.x() - ux * size - perp_x * (size * 0.4),
                     end_point.y() - uy * size - perp_y * (size * 0.4))
        painter.drawLine(end_point, pA)
        painter.drawLine(end_point, pB)

        # símbolo '+' cerca del cuerpo (en el punto medio del path)
        # Para simplificar, usamos el punto medio entre start y end
        mid_x = (start_point.x() + end_point.x()) / 2
        mid_y = (start_point.y() + end_point.y()) / 2
        pos = QPointF(mid_x, mid_y)

        painter.save()
        painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        painter.drawText(pos, "+")
        painter.restore()
