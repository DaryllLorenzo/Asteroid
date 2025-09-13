from PyQt6.QtWidgets import QGraphicsLineItem
from PyQt6.QtGui import QPen, QPolygonF, QColor
from PyQt6.QtCore import QPointF, QRectF, Qt
import math

class BaseEdgeItem(QGraphicsLineItem):
    """Item gráfico base para una arista con punta de flecha."""

    def __init__(self, source_node, dest_node, color=QColor(0, 0, 0), dashed=False):
        super().__init__()
        self.source_node = source_node
        self.dest_node = dest_node
        self.setFlag(QGraphicsLineItem.GraphicsItemFlag.ItemIsSelectable, True)

        # Configurar pen
        pen = QPen(color, 2)
        if dashed:
            pen.setStyle(Qt.PenStyle.DashLine)
        self.setPen(pen)

        self.update_position()

    def boundingRect(self):
        extra = (self.pen().width() + 20) / 2.0
        return QRectF(
            self.line().p1(), self.line().p2()
        ).normalized().adjusted(-extra, -extra, extra, extra)

    def update_position(self):
        """Recalcular posición entre los centros de los nodos."""
        if not self.source_node or not self.dest_node:
            return

        src_center = self.source_node.pos()
        dst_center = self.dest_node.pos()
        self.setLine(src_center.x(), src_center.y(), dst_center.x(), dst_center.y())

    def paint(self, painter, option, widget=None):
        if not self.source_node or not self.dest_node:
            return

        self.update_position()
        painter.setPen(self.pen())
        painter.drawLine(self.line())
        self._draw_arrow_head(painter)

    def _draw_arrow_head(self, painter):
        """Dibuja la punta de la flecha al final de la línea."""
        line = self.line()
        angle = math.atan2(line.dy(), line.dx())
        arrow_size = 10

        arrow_p1 = line.p2() - QPointF(
            arrow_size * math.cos(angle - math.pi / 6),
            arrow_size * math.sin(angle - math.pi / 6),
        )
        arrow_p2 = line.p2() - QPointF(
            arrow_size * math.cos(angle + math.pi / 6),
            arrow_size * math.sin(angle + math.pi / 6),
        )

        painter.setBrush(self.pen().color())
        painter.drawPolygon(QPolygonF([line.p2(), arrow_p1, arrow_p2]))
