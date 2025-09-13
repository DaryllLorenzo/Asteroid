from app.ui.components.base_node_item import BaseNodeItem
from app.core.models.entity.actor import Actor
from PyQt6.QtGui import QBrush, QPen, QColor

class ActorNodeItem(BaseNodeItem):
    def __init__(self, x=0, y=0, radius=50):
        super().__init__(Actor(x, y, radius))

    def paint(self, painter, option, widget=None):
        color = QColor(100, 150, 250)
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.drawEllipse(self.boundingRect())

        if self.model.show_subcanvas:
            painter.setBrush(QBrush(QColor(200, 200, 255, 50)))
            r = self.model.radius
            painter.drawEllipse(int(-r * 1.5), int(-r * 1.5), int(r * 3), int(r * 3))