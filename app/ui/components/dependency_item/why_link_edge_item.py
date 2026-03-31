# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------

# app/ui/components/dependency_item/why_link_edge_item.py
from PyQt6.QtGui import QPainter, QBrush, QColor, QFont, QFontMetrics, QPolygonF
from PyQt6.QtCore import QPointF, QRectF, Qt
import math
from app.ui.components.base_edge_item import BaseEdgeItem

class WhyLinkArrowItem(BaseEdgeItem):
    """Flecha tipo WHY: línea de extremo a extremo con triángulo en el medio y texto 'WHY' encima."""

    def __init__(self, source_node, dest_node):
        super().__init__(source_node, dest_node, color=QColor(0, 0, 0), dashed=False)

    def boundingRect(self):
        """Extiende el bounding rect para incluir la flecha y el texto."""
        extra = 20  # suficiente para triángulo + texto
        return super().boundingRect().adjusted(-extra, -extra, extra, extra)

    def paint(self, painter: QPainter, option, widget=None):
        if not self.source_node or not self.dest_node:
            return

        # NO llamar a update_position() aquí para evitar temblor
        path = self.path()
        if path.isEmpty():
            return

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(self.pen())
        painter.drawPath(path)

        # Triángulo y texto "WHY" en el punto MEDIO REAL del path curvo
        # Usamos el método utilitario para obtener el punto y ángulo correctos
        mid_point, mid_angle = self._get_point_at_percentage(0.5)
        
        # Ángulo del path en el punto medio
        angle = mid_angle
        size = 12.0
        
        # Dibujamos triángulo relleno apuntando en la dirección del path
        p_tip = mid_point
        p1 = QPointF(p_tip.x() - size * math.cos(angle - math.pi / 6),
                     p_tip.y() - size * math.sin(angle - math.pi / 6))
        p2 = QPointF(p_tip.x() - size * math.cos(angle + math.pi / 6),
                     p_tip.y() - size * math.sin(angle + math.pi / 6))

        painter.setBrush(QBrush(self.pen().color()))
        painter.drawPolygon(QPolygonF([p_tip, p1, p2]))

        # Texto "WHY" centrado encima de la flecha
        # Rotado para alinearse con el path
        font = QFont("Arial", 9)
        font.setBold(True)
        painter.setFont(font)
        fm = QFontMetrics(font)
        txt = "WHY"
        w = fm.horizontalAdvance(txt)
        h = fm.height()

        # Desplazamiento vertical para que no choque con el triángulo
        # Usamos coordenadas rotadas para alinear con el path
        painter.save()
        painter.translate(mid_point)
        painter.rotate(math.degrees(angle))
        
        # El texto se dibuja perpendicularmente arriba del path
        text_offset = size + 2
        text_rect = QRectF(-w / 2, -text_offset - h / 2, w, h)
        painter.setPen(self.pen().color())
        painter.drawText(text_rect, int(Qt.AlignmentFlag.AlignCenter), txt)
        painter.restore()
