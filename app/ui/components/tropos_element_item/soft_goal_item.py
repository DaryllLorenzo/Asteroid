# app/ui/components/tropos_element_item/soft_goal_item.py
from app.ui.components.base_node_item import BaseNodeItem
from app.core.models.tropos_element.soft_goal import SoftGoal
from PyQt6.QtGui import QBrush, QPen, QColor, QPainterPath
from PyQt6.QtCore import QRectF

class SoftGoalNodeItem(BaseNodeItem):
    def __init__(self, x=0, y=0, radius=50):
        super().__init__(SoftGoal(x, y, radius))
        self.scale_factor = 0.75  # valor para escalar tam de la nube
        self.path = self._create_cloud_path()

    def _create_cloud_path(self):
        r = self.model.radius * self.scale_factor
        cloud_parts = [
            (-r * 1.4, 0, r * 0.9),
            (-r * 0.9, -r * 0.4, r * 0.9),
            (-r * 0.5, 0, r * 0.8),
            (0, -r * 0.5, r * 1.0),
            (r * 0.5, 0, r * 0.8),
            (r * 0.9, -r * 0.4, r * 0.9),
            (r * 1.4, 0, r * 0.9),
            (-r * 0.7, r * 0.3, r * 0.6),
            (r * 0.7, r * 0.3, r * 0.6),
            (0, r * 0.2, r * 0.7),
        ]
        path = QPainterPath()
        for dx, dy, part_radius in cloud_parts:
            ellipse = QPainterPath()
            ellipse.addEllipse(dx - part_radius,
                               dy - part_radius,
                               part_radius * 2,
                               part_radius * 2)
            if path.isEmpty():
                path = ellipse
            else:
                path = path.united(ellipse)
        return path

    def boundingRect(self):
        return self.path.boundingRect().adjusted(-2, -2, 2, 2)

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(painter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(220, 220, 180)))
        painter.setPen(QPen(QColor(0, 0, 0), 3))
        painter.drawPath(self.path)
