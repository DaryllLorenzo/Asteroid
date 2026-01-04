# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------

from app.ui.components.base_tropos_item import BaseTroposItem
from app.core.models.tropos_element.soft_goal import SoftGoal
from PyQt6.QtGui import QBrush, QPen, QColor, QPainterPath, QFont
from PyQt6.QtCore import QRectF, QPointF, Qt
import math

class SoftGoalNodeItem(BaseTroposItem):
    def __init__(self, x=0, y=0, radius=30):
        super().__init__(SoftGoal(x, y, radius))
        self.model.radius = radius
        self.path = self._create_cloud_path()

    def _create_cloud_path(self):
        path = QPainterPath()
        r = float(self.model.radius)
        w = r * 2.8 
        h = r * 0.95
        
        path.moveTo(-w * 0.85, 0)
        path.cubicTo(-w * 1.05, -h * 0.8, -w * 0.75, -h * 1.3, -w * 0.35, -h * 0.85)
        path.cubicTo(-w * 0.15, -h * 1.25, w * 0.15, -h * 1.25, w * 0.35, -h * 0.85)
        path.cubicTo(w * 0.75, -h * 1.3, w * 1.05, -h * 0.8, w * 0.85, 0)
        path.cubicTo(w * 1.05,  h * 0.8, w * 0.75,  h * 1.3, w * 0.35,  h * 0.85)
        path.cubicTo(w * 0.15,  h * 1.25, -w * 0.15,  h * 1.25, -w * 0.35,  h * 0.85)
        path.cubicTo(-w * 0.75,  h * 1.3, -w * 1.05,  h * 0.8, -w * 0.85,  0)
        path.closeSubpath()
        return path

    def boundingRect(self):
        if not hasattr(self, "path") or self.path.isEmpty():
            r = self.model.radius
            return QRectF(-r, -r, r*2, r*2)
        return self.path.boundingRect().adjusted(-2, -2, 2, 2)

    def _get_distance_to_border(self, pos: QPointF) -> float:
        """Distancia aproximada al borde de la nube."""
        if hasattr(self, 'path') and not self.path.isEmpty():
            # Crear un stroker para simular el borde
            from PyQt6.QtGui import QPen, QPainterPathStroker
            stroker = QPainterPathStroker()
            stroker.setWidth(10)  # Ancho del área de detección
            
            # Crear path para el borde
            stroke_path = stroker.createStroke(self.path)
            
            # Si el punto está en el borde, distancia = 0
            if stroke_path.contains(pos):
                return 0
            else:
                # Calcular distancia al bounding rect como aproximación
                br = self.path.boundingRect()
                center = br.center()
                dist_to_center = math.sqrt((pos.x() - center.x())**2 + (pos.y() - center.y())**2)
                # Aproximación simple
                return abs(dist_to_center - self.model.radius)
        return super()._get_distance_to_border(pos)

    def _get_new_radius_from_pos(self, pos: QPointF) -> float:
        return max((pos.x()**2 + pos.y()**2) ** 0.5, 15.0)

    def set_radius(self, new_r: float):
        super().set_radius(new_r)
        self.path = self._create_cloud_path()

    def paint(self, painter, option, widget=None):
        default_color = QColor(220, 220, 180)
        default_border = QColor(0, 0, 0)
        default_text = QColor(0, 0, 0)
        
        fill_color = QColor(self.model.color) if hasattr(self.model, 'color') else default_color
        border_color = QColor(self.model.border_color) if hasattr(self.model, 'border_color') else default_border
        text_color = QColor(self.model.text_color) if hasattr(self.model, 'text_color') else default_text
        
        painter.setRenderHint(painter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(fill_color))
        painter.setPen(QPen(border_color, 2))
        painter.drawPath(self.path)

        # DIBUJAR TEXTO MULTILÍNEA
        # El texto se dibujará centrado sobre la nube
        self.draw_multiline_text(painter, text_color)

        if self.isSelected():
            painter.setPen(QPen(Qt.GlobalColor.yellow, 3))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(self.path)

    def get_serializable_properties(self):
        base_properties = super().get_serializable_properties()
        base_properties['node_type'] = 'soft_goal'
        return base_properties

    def update_properties(self, properties: dict):
        super().update_properties(properties)