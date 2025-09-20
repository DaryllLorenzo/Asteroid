# app/ui/components/tropos_element_item/plan_item.py
from app.ui.components.base_node_item import BaseNodeItem
from app.core.models.tropos_element.plan import Plan
from PyQt6.QtGui import QBrush, QPen, QColor
from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QPolygonF

class PlanNodeItem(BaseNodeItem):
    def __init__(self, x=0, y=0, radius=50):
        super().__init__(Plan(x, y, radius))

    def paint(self, painter, option, widget=None):
        painter.setBrush(QBrush(QColor(150, 180, 250)))
        painter.setPen(QPen(QColor(0, 0, 0), 2))

        r = self.model.radius
        points = [
            QPointF(-r, 0), QPointF(-r/2, -r/2), QPointF(r/2, -r/2),
            QPointF(r, 0), QPointF(r/2, r/2), QPointF(-r/2, r/2)
        ]
        painter.drawPolygon(QPolygonF(points))
