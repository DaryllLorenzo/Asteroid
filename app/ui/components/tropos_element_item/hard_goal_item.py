# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------

from app.ui.components.base_tropos_item import BaseTroposItem
from app.core.models.tropos_element.hard_goal import HardGoal
from PyQt6.QtGui import QBrush, QPen, QColor, QPainterPath, QFont
from PyQt6.QtCore import QRectF, QPointF, Qt
import math

class HardGoalNodeItem(BaseTroposItem):
    def __init__(self, x=0, y=0, radius=60):
        super().__init__(HardGoal(x, y, radius))

    def _get_distance_to_border(self, pos: QPointF) -> float:
        """Distancia exacta al borde de la píldora."""
        r = self.model.radius
        rect = QRectF(-r, -r/2, 2 * r, r)
        
        # Si el punto está dentro del rectángulo, calcular distancia al borde más cercano
        if rect.contains(pos):
            # Distancia a los bordes horizontal y vertical
            dist_left = abs(pos.x() - rect.left())
            dist_right = abs(pos.x() - rect.right())
            dist_top = abs(pos.y() - rect.top())
            dist_bottom = abs(pos.y() - rect.bottom())
            return min(dist_left, dist_right, dist_top, dist_bottom)
        else:
            # Si está fuera, calcular distancia al rectángulo redondeado
            # Simplificación: usar distancia al rectángulo principal
            dx = max(rect.left() - pos.x(), 0, pos.x() - rect.right())
            dy = max(rect.top() - pos.y(), 0, pos.y() - rect.bottom())
            return math.sqrt(dx*dx + dy*dy)

    def _get_new_radius_from_pos(self, pos: QPointF) -> float:
        """Calcula nuevo 'radio' basado en la distancia horizontal (ancho de la píldora)."""
        # La píldora tiene ancho = 2 * r, así que r = ancho / 2
        # Usamos la coordenada X como principal (porque es horizontal)
        new_r = abs(pos.x())
        return max(new_r, 20.0)  # mínimo r=20

    def paint(self, painter, option, widget=None):
        # ✅ USAR COLORES PERSONALIZADOS del modelo, pero mantener el verde por defecto si no están personalizados
        default_color = QColor(150, 200, 150)  # Tu verde original
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
        path = QPainterPath()
        path.addRoundedRect(rect, r/2, r/2)
        painter.drawPath(path)

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
            painter.drawPath(path)

    def get_serializable_properties(self):
        """Devuelve propiedades serializables específicas de HardGoal"""
        base_properties = super().get_serializable_properties()
        base_properties['node_type'] = 'hard_goal'  # Para identificar el tipo al cargar
        # Agrega propiedades específicas de HardGoal aquí si las tienes
        return base_properties

    def update_properties(self, properties: dict):
        """Actualiza propiedades específicas de HardGoal"""
        # Primero actualiza las propiedades base
        super().update_properties(properties)