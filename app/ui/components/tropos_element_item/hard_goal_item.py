# app/ui/components/tropos_element_item/hard_goal_item.py
from app.ui.components.base_tropos_item import BaseTroposItem
from app.core.models.tropos_element.hard_goal import HardGoal
from PyQt6.QtGui import QBrush, QPen, QColor, QPainterPath
from PyQt6.QtCore import QRectF

class HardGoalNodeItem(BaseTroposItem):
    def __init__(self, x=0, y=0, radius=60):
        super().__init__(HardGoal(x, y, radius))

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(painter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(150, 200, 150)))
        painter.setPen(QPen(QColor(0, 0, 0), 2))

        # "Pill shape" → óvalo alargado
        r = self.model.radius
        rect = QRectF(-r, -r/2, 2*r, r)
        path = QPainterPath()
        path.addRoundedRect(rect, r/2, r/2)
        painter.drawPath(path)
