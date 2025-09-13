from PyQt6.QtGui import QColor
from app.ui.components.base_edge_item import BaseEdgeItem

class SimpleArrowItem(BaseEdgeItem):
    def __init__(self, source_node, dest_node):
        super().__init__(source_node, dest_node, color=QColor(0, 0, 0), dashed=False)
