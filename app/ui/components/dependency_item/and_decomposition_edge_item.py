# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------

from PyQt6.QtGui import QPainter, QPen, QPolygonF
from PyQt6.QtCore import QPointF, Qt
import math
from app.ui.components.base_edge_item import BaseEdgeItem

class AndDecompositionArrowItem(BaseEdgeItem):
    """Barra (T) cerca del final + cabeza triangular sin relleno."""

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

        # Tamaño de la cabeza de flecha
        arrow_size = 12.0

        # Calcular ángulo y vectores unitarios
        end_point = self._end_point
        start_point = self._start_point
        
        dx = end_point.x() - start_point.x()
        dy = end_point.y() - start_point.y()
        
        if dx == 0 and dy == 0:
            return
        
        angle = math.atan2(dy, dx)
        ux = math.cos(angle)
        uy = math.sin(angle)
        perp_x = -uy
        perp_y = ux

        # Línea ajustada para terminar antes de la flecha
        p_start = start_point
        p_tip = end_point
        p_line_end = QPointF(p_tip.x() - arrow_size * ux,
                             p_tip.y() - arrow_size * uy)
        painter.drawLine(p_start, p_line_end)

        # Barra vertical (T) en 60% de la línea visible
        t_factor = 0.6
        pos_x = p_start.x() + (p_line_end.x() - p_start.x()) * t_factor
        pos_y = p_start.y() + (p_line_end.y() - p_start.y()) * t_factor
        pos = QPointF(pos_x, pos_y)

        half = 6.0
        pa = QPointF(pos.x() - perp_x * half, pos.y() - perp_y * half)
        pb = QPointF(pos.x() + perp_x * half, pos.y() + perp_y * half)
        painter.drawLine(pa, pb)

        # Cabeza triangular sin relleno
        base = p_line_end
        corner1 = QPointF(base.x() + perp_x * (0.5 * arrow_size),
                          base.y() + perp_y * (0.5 * arrow_size))
        corner2 = QPointF(base.x() - perp_x * (0.5 * arrow_size),
                          base.y() - perp_y * (0.5 * arrow_size))

        poly = QPolygonF([p_tip, corner1, corner2])
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPolygon(poly)
