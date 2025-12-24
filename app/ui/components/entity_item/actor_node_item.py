# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------
from app.ui.components.base_node_item import BaseNodeItem
from app.core.models.entity.actor import Actor
from PyQt6.QtGui import QBrush, QPen, QColor, QFont
from PyQt6.QtCore import Qt, QPointF

class ActorNodeItem(BaseNodeItem):
    def __init__(self, x=0, y=0, radius=50):
        super().__init__(Actor(x, y, radius))
        
    def paint(self, painter, option, widget=None):
        # 1. Configuración de colores
        default_color = QColor(100, 150, 250)  # Azul
        default_border = QColor(0, 0, 0)       # Negro
        default_text = QColor(255, 255, 255)    # Blanco
        
        fill_color = QColor(self.model.color) if hasattr(self.model, 'color') else default_color
        border_color = QColor(self.model.border_color) if hasattr(self.model, 'border_color') else default_border
        text_color = QColor(self.model.text_color) if hasattr(self.model, 'text_color') else default_text
        
        # 2. DIBUJAR EL CONTENEDOR (Círculo base)
        painter.setBrush(QBrush(fill_color))
        painter.setPen(QPen(border_color, 2))
        painter.drawEllipse(self.boundingRect())
    
        # 3. DIBUJAR EL CONTENIDO (Texto con desplazamiento interno)
        content_off_x = getattr(self.model, 'content_offset_x', 0.0) * self.model.radius
        content_off_y = getattr(self.model, 'content_offset_y', 0.0) * self.model.radius
    
        painter.save()
        painter.translate(content_off_x, content_off_y)
    
        if hasattr(self.model, 'label') and self.model.label:
            painter.setPen(QPen(text_color))
            font = QFont()
            font.setPointSize(10)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(self.boundingRect(), Qt.AlignmentFlag.AlignCenter, self.model.label)
        
        painter.restore()
    
        # 4. Indicador de selección
        if self.isSelected():
            painter.setPen(QPen(Qt.GlobalColor.yellow, 3))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(self.boundingRect())

    def get_serializable_properties(self):
        base_properties = super().get_serializable_properties()
        base_properties['node_type'] = 'actor'
        # Incluimos los offsets para asegurar consistencia
        base_properties['content_offset_x'] = getattr(self.model, 'content_offset_x', 0.0)
        base_properties['content_offset_y'] = getattr(self.model, 'content_offset_y', 0.0)
        
        # 🚀 NUEVO: Incluir posición en subcanvas
        base_properties['position_in_subcanvas_x'] = getattr(self.model, 'position_in_subcanvas_x', 0.0)
        base_properties['position_in_subcanvas_y'] = getattr(self.model, 'position_in_subcanvas_y', 0.0)
        
        return base_properties

    def update_properties(self, properties: dict):
        super().update_properties(properties)
        # Forzamos repintado por si cambiaron los offsets o posición en subcanvas
        self.update()