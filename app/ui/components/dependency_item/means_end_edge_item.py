# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------

# app/ui/components/dependency_item/means_end_edge_item.py
from PyQt6.QtGui import QPainter, QPen
from PyQt6.QtCore import QPointF, QRectF
import math

from app.ui.components.base_edge_item import BaseEdgeItem

class MeansEndArrowItem(BaseEdgeItem):
    """Flecha abierta tipo V sin símbolo (means-end)."""

    def __init__(self, source_node, dest_node):
        super().__init__(source_node, dest_node, color=QPen().color(), dashed=False)

    def boundingRect(self):
        """Extiende el bounding rect para incluir la cabeza de flecha en V."""
        # Obtener boundingRect base de la línea
        base_rect = super().boundingRect()
        # Extra para la V abierta (~12px)
        extra = 15
        return base_rect.adjusted(-extra, -extra, extra, extra)

    def paint(self, painter: QPainter, option, widget=None):
        if not self.source_node or not self.dest_node:
            return

        # NO llamar a update_position() aquí para evitar temblor
        path = self.path()
        if path.isEmpty():
            return

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(self.pen())
        painter.drawPath(path)

        end_point = self._end_point
        
        # Determinar el último segmento para calcular el ángulo
        if self.control_points:
            last_point = self.control_points[-1]
        else:
            last_point = self._start_point
        
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

        pA = QPointF(end_point.x() - ux * size + perp_x * (size * 0.4),
                     end_point.y() - uy * size + perp_y * (size * 0.4))
        pB = QPointF(end_point.x() - ux * size - perp_x * (size * 0.4),
                     end_point.y() - uy * size - perp_y * (size * 0.4))
        painter.drawLine(end_point, pA)
        painter.drawLine(end_point, pB)
