from app.ui.components.base_node_item import BaseNodeItem
from app.core.models.entity.agent import Agent
from PyQt6.QtGui import QBrush, QPen, QColor


class AgentNodeItem(BaseNodeItem):
    def __init__(self, x=0, y=0, radius=50):
        super().__init__(Agent(x, y, radius))

    def paint(self, painter, option, widget=None):
        color = QColor(250, 150, 100)
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.drawEllipse(self.boundingRect())

        y_position = int(-self.model.radius * 0.3)
        painter.drawLine(int(-self.model.radius), y_position, int(self.model.radius), y_position)

        if self.model.show_subcanvas:
            painter.setBrush(QBrush(QColor(255, 200, 150, 50)))
            r = self.model.radius
            painter.drawEllipse(int(-r * 1.5), int(-r * 1.5), int(r * 3), int(r * 3))