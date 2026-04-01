# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------

# app/ui/components/dependency_item/or_decomposition_edge_item.py
from PyQt6.QtGui import QPainter, QPen, QPolygonF, QPainterPath
from PyQt6.QtCore import QPointF, Qt, QRectF
import math

from app.ui.components.base_edge_item import BaseEdgeItem

class OrDecompositionArrowItem(BaseEdgeItem):
    """Cabeza triangular sin relleno en la punta (OR)."""

    def __init__(self, source_node, dest_node):
        super().__init__(source_node, dest_node, color=QPen().color(), dashed=False)

    def boundingRect(self):
        """Extiende el bounding rect para incluir la cabeza de flecha triangular."""
        # Obtener boundingRect base de la línea
        base_rect = super().boundingRect()
        # Extra para la cabeza de flecha (triángulo de ~12px)
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

        # Calcular el punto donde termina la línea (base del triángulo)
        line_end_point = QPointF(end_point.x() - size * math.cos(angle),
                                 end_point.y() - size * math.sin(angle))

        # Crear un path modificado que termine en la base del triángulo
        # Obtener todos los puntos del path original (ya en coordenadas locales)
        path_points, start_point, _ = self._calculate_path_points()

        if len(path_points) >= 2:
            # Si hay control points, el último segmento va del último control point al end_point
            # Reemplazamos el último punto con line_end_point
            if self.control_points:
                modified_points = path_points[:-1] + [line_end_point]
            else:
                modified_points = [start_point, line_end_point]

            # Los puntos ya están en coordenadas locales
            modified_path = QPainterPath(modified_points[0])
            for point in modified_points[1:]:
                modified_path.lineTo(point)

            # Dibujar el path modificado (línea que termina antes)
            painter.drawPath(modified_path)
        else:
            # Fallback: dibujar path original
            painter.drawPath(path)

        # Dibujar triángulo sin relleno en la punta
        perp_x = math.sin(angle) * (size * 0.5)
        perp_y = -math.cos(angle) * (size * 0.5)

        p_tip = end_point
        p_base = line_end_point

        p1 = QPointF(p_base.x() + perp_x, p_base.y() + perp_y)
        p2 = QPointF(p_base.x() - perp_x, p_base.y() - perp_y)

        poly = QPolygonF([p_tip, p1, p2])
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPolygon(poly)
