# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------
from app.ui.components.base_node_item import BaseNodeItem
from app.core.models.entity.agent import Agent
from PyQt6.QtGui import QBrush, QPen, QColor, QFont
from PyQt6.QtCore import QPointF, Qt

class AgentNodeItem(BaseNodeItem):
    def __init__(self, x=0, y=0, radius=50):
        super().__init__(Agent(x, y, radius))
        
    def _get_distance_to_border(self, pos: QPointF) -> float:
        r = getattr(self.model, "radius", 50)
        center_dist = (pos.x()**2 + pos.y()**2) ** 0.5
        return abs(center_dist - r)

    def paint(self, painter, option, widget=None):
        # 1. Colores
        default_color = QColor(250, 150, 100)  # Naranja
        default_border = QColor(0, 0, 0)       # Negro
        default_text = QColor(255, 255, 255)    # Blanco
        
        fill_color = QColor(self.model.color) if hasattr(self.model, 'color') else default_color
        border_color = QColor(self.model.border_color) if hasattr(self.model, 'border_color') else default_border
        text_color = QColor(self.model.text_color) if hasattr(self.model, 'text_color') else default_text
        
        # 2. DIBUJAR EL CONTENEDOR (Círculo base)
        painter.setBrush(QBrush(fill_color))
        painter.setPen(QPen(border_color, 2))
        painter.drawEllipse(self.boundingRect())
    
        # 3. DIBUJAR EL CONTENIDO DESPLAZADO (Texto + Línea)
        content_off_x = getattr(self.model, 'content_offset_x', 0.0) * self.model.radius
        content_off_y = getattr(self.model, 'content_offset_y', 0.0) * self.model.radius
    
        painter.save()
        painter.translate(content_off_x, content_off_y)
    
        # Texto del Agente
        if hasattr(self.model, 'label') and self.model.label:
            painter.setPen(QPen(text_color))
            font = QFont()
            font.setPointSize(10)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(self.boundingRect(), Qt.AlignmentFlag.AlignCenter, self.model.label)
    
        # La línea característica del agente (también se desplaza)
        y_position = int(-self.model.radius * 0.3)
        painter.setPen(QPen(border_color, 2))
        painter.drawLine(int(-self.model.radius), y_position, int(self.model.radius), y_position)
        
        painter.restore()
    
        # 4. Indicador de selección
        if self.isSelected():
            painter.setPen(QPen(Qt.GlobalColor.yellow, 3))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(self.boundingRect())

    def get_serializable_properties(self):
        base_properties = super().get_serializable_properties()
        base_properties['node_type'] = 'agent'
        base_properties['content_offset_x'] = getattr(self.model, 'content_offset_x', 0.0)
        base_properties['content_offset_y'] = getattr(self.model, 'content_offset_y', 0.0)
        
        # 🚀 NUEVO: Incluir posición en subcanvas
        base_properties['position_in_subcanvas_x'] = getattr(self.model, 'position_in_subcanvas_x', 0.0)
        base_properties['position_in_subcanvas_y'] = getattr(self.model, 'position_in_subcanvas_y', 0.0)
        
        return base_properties

    def update_properties(self, properties: dict):
        super().update_properties(properties)
        self.update()