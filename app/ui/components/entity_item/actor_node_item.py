# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------

from app.ui.components.base_node_item import BaseNodeItem
from app.core.models.entity.actor import Actor
from PyQt6.QtGui import QBrush, QPen, QColor, QFont
from PyQt6.QtCore import Qt

class ActorNodeItem(BaseNodeItem):
    def __init__(self, x=0, y=0, radius=50):
        super().__init__(Actor(x, y, radius))

    def paint(self, painter, option, widget=None):
        # ✅ USAR COLORES PERSONALIZADOS del modelo, pero mantener el azul por defecto si no están personalizados
        default_color = QColor(100, 150, 250)  # Tu azul original
        default_border = QColor(0, 0, 0)       # Tu borde negro original
        default_text = QColor(255, 255, 255)   # Texto blanco
        
        # Usar colores del modelo si existen, si no usar defaults
        fill_color = QColor(self.model.color) if hasattr(self.model, 'color') else default_color
        border_color = QColor(self.model.border_color) if hasattr(self.model, 'border_color') else default_border
        text_color = QColor(self.model.text_color) if hasattr(self.model, 'text_color') else default_text
        
        painter.setBrush(QBrush(fill_color))
        painter.setPen(QPen(border_color, 2))
        painter.drawEllipse(self.boundingRect())

        # Dibujar texto si el nodo tiene label
        if hasattr(self.model, 'label') and self.model.label:
            painter.setPen(QPen(text_color))
            font = QFont()
            font.setPointSize(10)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(self.boundingRect(), Qt.AlignmentFlag.AlignCenter, self.model.label)

        # Indicador de selección
        if self.isSelected():
            painter.setPen(QPen(Qt.GlobalColor.yellow, 3))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(self.boundingRect())

    def get_serializable_properties(self):
        """Devuelve propiedades serializables específicas de Actor"""
        base_properties = super().get_serializable_properties()
        # Agrega propiedades específicas de Actor aquí si las tienes
        base_properties['node_type'] = 'actor'  # Para identificar el tipo al cargar
        return base_properties
    
    def update_properties(self, properties: dict):
        """Actualiza propiedades específicas de Actor"""
        # Primero actualiza las propiedades base
        super().update_properties(properties)