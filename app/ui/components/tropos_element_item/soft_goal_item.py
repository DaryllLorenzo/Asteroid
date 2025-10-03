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
        r = float(self.model.radius)
        cloud_parts = [
            (-r*1.4, 0, r*0.9),
            (-r*0.9, -r*0.4, r*0.9),
            (-r*0.5, 0, r*0.8),
            (0, -r*0.5, r*1.0),
            (r*0.5, 0, r*0.8),
            (r*0.9, -r*0.4, r*0.9),
            (r*1.4, 0, r*0.9),
            (-r*0.7, r*0.3, r*0.6),
            (r*0.7, r*0.3, r*0.6),
            (0, r*0.2, r*0.7),
        ]
        p = QPainterPath()
        for dx, dy, pr in cloud_parts:
            ellipse = QPainterPath()
            ellipse.addEllipse(dx - pr, dy - pr, pr*2, pr*2)
            p = p.united(ellipse) if not p.isEmpty() else ellipse
        return p

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
        """Nuevo radio basado en distancia al centro."""
        return max((pos.x()**2 + pos.y()**2) ** 0.5, 15.0)

    def set_radius(self, new_r: float):
        # Llamar al método de la clase base para actualizar el radio y preparar el cambio de geometría
        super().set_radius(new_r)
        # Regenerar el path con el nuevo radio
        self.path = self._create_cloud_path()

    def paint(self, painter, option, widget=None):
        # ✅ USAR COLORES PERSONALIZADOS del modelo, pero mantener el color beige por defecto si no están personalizados
        default_color = QColor(220, 220, 180)  # Tu beige original
        default_border = QColor(0, 0, 0)       # Borde negro original
        default_text = QColor(0, 0, 0)         # Texto negro (porque el fondo es claro)
        
        fill_color = QColor(self.model.color) if hasattr(self.model, 'color') else default_color
        border_color = QColor(self.model.border_color) if hasattr(self.model, 'border_color') else default_border
        text_color = QColor(self.model.text_color) if hasattr(self.model, 'text_color') else default_text
        
        painter.setRenderHint(painter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(fill_color))
        painter.setPen(QPen(border_color, 2))
        painter.drawPath(self.path)

        # Dibujar texto
        if hasattr(self.model, 'label') and self.model.label:
            painter.setPen(QPen(text_color))
            font = QFont()
            font.setPointSize(9)
            font.setBold(True)
            painter.setFont(font)
            # Usar el boundingRect del path para centrar el texto
            text_rect = self.path.boundingRect()
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, self.model.label)

        # Indicador de selección
        if self.isSelected():
            painter.setPen(QPen(Qt.GlobalColor.yellow, 3))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(self.path)