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

        # Actualizamos la línea entre nodos
        self.update_position()
        line = self.line()
        if line.length() == 0:
            return

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(self.pen())
        painter.drawLine(line)

        # Triángulo en el punto medio de la línea
        mid_x = (line.x1() + line.x2()) / 2
        mid_y = (line.y1() + line.y2()) / 2
        p_tip = QPointF(mid_x, mid_y)

        # Ángulo de la línea
        angle = math.atan2(line.dy(), line.dx())
        size = 12.0
        p1 = QPointF(p_tip.x() - size * math.cos(angle - math.pi / 6),
                     p_tip.y() - size * math.sin(angle - math.pi / 6))
        p2 = QPointF(p_tip.x() - size * math.cos(angle + math.pi / 6),
                     p_tip.y() - size * math.sin(angle + math.pi / 6))

        # Dibujamos triángulo relleno
        painter.setBrush(QBrush(self.pen().color()))
        painter.drawPolygon(QPolygonF([p_tip, p1, p2]))

        # Texto "WHY" centrado encima de la flecha
        font = QFont("Arial", 9)
        font.setBold(True)
        painter.setFont(font)
        fm = QFontMetrics(font)
        txt = "WHY"
        w = fm.horizontalAdvance(txt)
        h = fm.height()

        # Desplazamiento vertical para que no choque con el triángulo
        text_offset = size + 2
        text_rect = QRectF(mid_x - w / 2, mid_y - text_offset - h / 2, w, h)
        painter.setPen(self.pen().color())
        painter.drawText(text_rect, int(Qt.AlignmentFlag.AlignCenter), txt)
