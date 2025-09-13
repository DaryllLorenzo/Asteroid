from PyQt6.QtGui import QColor
from app.ui.components.base_edge_item import BaseEdgeItem

class DashedArrowItem(BaseEdgeItem):
    def __init__(self, source_node, dest_node):
        super().__init__(source_node, dest_node, color=QColor(100, 100, 100), dashed=True)
