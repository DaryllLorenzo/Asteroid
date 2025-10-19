# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------

from app.ui.components.base_tropos_item import BaseTroposItem
from app.core.models.tropos_element.resource import Resource
from PyQt6.QtGui import QBrush, QPen, QColor, QFont
from PyQt6.QtCore import QRectF, QPointF, Qt
import math

class ResourceNodeItem(BaseTroposItem):
    def __init__(self, x=0, y=0, radius=50):
        super().__init__(Resource(x, y, radius))

    def _get_distance_to_border(self, pos: QPointF) -> float:
        """Distancia exacta al borde del rectángulo."""
        r = self.model.radius
        rect = QRectF(-r, -r/2, 2 * r, r)
        
        # Si el punto está dentro, calcular distancia al borde más cercano
        if rect.contains(pos):
            dist_left = abs(pos.x() - rect.left())
            dist_right = abs(pos.x() - rect.right())
            dist_top = abs(pos.y() - rect.top())
            dist_bottom = abs(pos.y() - rect.bottom())
            return min(dist_left, dist_right, dist_top, dist_bottom)
        else:
            # Si está fuera, calcular distancia al rectángulo
            dx = max(rect.left() - pos.x(), 0, pos.x() - rect.right())
            dy = max(rect.top() - pos.y(), 0, pos.y() - rect.bottom())
            return math.sqrt(dx*dx + dy*dy)

    def _get_new_radius_from_pos(self, pos: QPointF) -> float:
        """Nuevo radio basado en la coordenada X (ancho del rectángulo)."""
        new_r = abs(pos.x())
        return max(new_r, 20.0)

    def paint(self, painter, option, widget=None):
        # ✅ USAR COLORES PERSONALIZADOS del modelo, pero mantener el lila por defecto si no están personalizados
        default_color = QColor(200, 150, 250)  # Tu lila original
        default_border = QColor(0, 0, 0)       # Borde negro original
        default_text = QColor(255, 255, 255)   # Texto blanco
        
        fill_color = QColor(self.model.color) if hasattr(self.model, 'color') else default_color
        border_color = QColor(self.model.border_color) if hasattr(self.model, 'border_color') else default_border
        text_color = QColor(self.model.text_color) if hasattr(self.model, 'text_color') else default_text
        
        painter.setRenderHint(painter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(fill_color))
        painter.setPen(QPen(border_color, 2))

        r = self.model.radius
        rect = QRectF(-r, -r/2, 2 * r, r)
        painter.drawRect(rect)

        # Dibujar texto
        if hasattr(self.model, 'label') and self.model.label:
            painter.setPen(QPen(text_color))
            font = QFont()
            font.setPointSize(10)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.model.label)

        # Indicador de selección
        if self.isSelected():
            painter.setPen(QPen(Qt.GlobalColor.yellow, 3))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(rect)

    def get_serializable_properties(self):
        """Devuelve propiedades serializables específicas de Resource"""
        base_properties = super().get_serializable_properties()
        base_properties['node_type'] = 'resource'
        return base_properties

    def update_properties(self, properties: dict):
        """Actualiza propiedades específicas de Resource"""
        super().update_properties(properties)