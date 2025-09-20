# app/ui/components/tropos_element_item/resource_item.py
from app.ui.components.base_node_item import BaseNodeItem
from app.core.models.tropos_element.resource import Resource
from PyQt6.QtGui import QBrush, QPen, QColor
from PyQt6.QtCore import QRectF

class ResourceNodeItem(BaseNodeItem):
    def __init__(self, x=0, y=0, radius=50):
        super().__init__(Resource(x, y, radius))

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(painter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(200, 150, 250)))
        painter.setPen(QPen(QColor(0, 0, 0), 2))

        r = self.model.radius
        painter.drawRect(QRectF(-r, -r/2, 2*r, r))