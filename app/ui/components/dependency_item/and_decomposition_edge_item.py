# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------

from PyQt6.QtGui import QPainter, QPen, QPolygonF, QPainterPath
from PyQt6.QtCore import QPointF, Qt, QRectF
import math
from app.ui.components.base_edge_item import BaseEdgeItem

class AndDecompositionArrowItem(BaseEdgeItem):
    """Barra (T) cerca del final + cabeza triangular sin relleno."""

    def __init__(self, source_node, dest_node):
        super().__init__(source_node, dest_node, color=QPen().color(), dashed=False)

    def boundingRect(self):
        """Extiende el bounding rect para incluir la cabeza de flecha y la barra T."""
        # Obtener boundingRect base de la línea
        base_rect = super().boundingRect()
        # Extra para la cabeza de flecha (~12px) y la barra T
        extra = 20
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
        arrow_size = 12.0

        # Calcular ángulo y vectores unitarios usando el último segmento real
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
        perp_x = -math.sin(angle)
        perp_y = math.cos(angle)

        # Calcular el punto donde termina la línea (base del triángulo)
        line_end_point = QPointF(end_point.x() - arrow_size * math.cos(angle),
                                 end_point.y() - arrow_size * math.sin(angle))
        
        # Crear un path modificado que termine en la base del triángulo
        # Obtener todos los puntos del path original
        path_points, start_point, _ = self._calculate_path_points()
        
        if len(path_points) >= 2:
            # Si hay control points, el último segmento va del último control point al end_point
            # Reemplazamos el último punto con line_end_point
            if self.control_points:
                modified_points = path_points[:-1] + [line_end_point]
            else:
                modified_points = [start_point, line_end_point]
            
            # Crear path modificado en coordenadas locales
            if self.scene():
                local_points = [self.mapFromScene(p) for p in modified_points]
            else:
                local_points = modified_points
            
            modified_path = QPainterPath(local_points[0])
            for point in local_points[1:]:
                modified_path.lineTo(point)
            
            # Dibujar el path modificado (línea que termina antes)
            painter.drawPath(modified_path)
        else:
            # Fallback: dibujar path original
            painter.drawPath(path)

        # Cabeza triangular sin relleno en la punta
        p_tip = end_point
        base = line_end_point
        
        corner1 = QPointF(base.x() + perp_x * (0.5 * arrow_size),
                          base.y() + perp_y * (0.5 * arrow_size))
        corner2 = QPointF(base.x() - perp_x * (0.5 * arrow_size),
                          base.y() - perp_y * (0.5 * arrow_size))

        poly = QPolygonF([p_tip, corner1, corner2])
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPolygon(poly)

        # Barra vertical (T) en el 60% REAL del path curvo
        # Usamos el método utilitario para obtener el punto y ángulo correctos
        bar_point, bar_angle = self._get_point_at_percentage(0.6)
        
        # La barra debe ser perpendicular al path en ese punto
        half = 6.0
        # Perpendicular al ángulo del path
        bar_perp_x = -math.sin(bar_angle)
        bar_perp_y = math.cos(bar_angle)
        
        pa = QPointF(bar_point.x() - bar_perp_x * half, bar_point.y() - bar_perp_y * half)
        pb = QPointF(bar_point.x() + bar_perp_x * half, bar_point.y() + bar_perp_y * half)
        painter.drawLine(pa, pb)
