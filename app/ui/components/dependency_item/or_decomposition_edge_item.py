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

        # NO llamar a update_position() aquí para evitar temblor
        path = self.path()
        if path.isEmpty():
            return

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(self.pen())

        # El path completo (con curvas) ya se dibuja aquí
        painter.drawPath(path)

        # Tamaño de la cabeza de flecha
        size = 12.0

        # Calcular ángulo usando el ÚLTIMO segmento real del path curvo
        end_point = self._end_point
        
        # Determinar el último segmento para calcular el ángulo correcto
        if self.control_points:
            last_point = self.control_points[-1]
        else:
            last_point = self._start_point

        dx = end_point.x() - last_point.x()
        dy = end_point.y() - last_point.y()

        if dx == 0 and dy == 0:
            return

        angle = math.atan2(dy, dx)
        
        # Solo dibujar el triángulo sin relleno en la punta
        # La línea ya está dibujada por painter.drawPath(path)
        perp_x = math.sin(angle) * (size * 0.5)
        perp_y = -math.cos(angle) * (size * 0.5)
        
        # El triángulo termina un poco antes del end_point para que se vea la punta
        p_tip = end_point
        p_base = QPointF(end_point.x() - size * math.cos(angle),
                         end_point.y() - size * math.sin(angle))
        
        p1 = QPointF(p_base.x() + perp_x, p_base.y() + perp_y)
        p2 = QPointF(p_base.x() - perp_x, p_base.y() - perp_y)

        poly = QPolygonF([p_tip, p1, p2])
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPolygon(poly)
