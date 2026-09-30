# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush
from PyQt6.QtGui import QColor
from PyQt6.QtGui import QPen

from app.core.models.typed_node import TypedNode
from app.ui.components.base_node_item import BaseNodeItem
from app.ui.theme_manager import theme_manager


class ActorNodeItem(BaseNodeItem):
    def __init__(self, x=0, y=0, radius=50):
        super().__init__(TypedNode("actor", x, y, radius))

    def paint(self, painter, option, widget=None):
        clipped = self.apply_subcanvas_clipping(painter)

        default_color = QColor(100, 150, 250)
        default_border = QColor(0, 0, 0)
        default_text = QColor(255, 255, 255)

        fill_color = (
            QColor(self.model.color) if hasattr(self.model, "color") else default_color
        )
        if theme_manager().is_dark:
            border_color = QColor("#ffffff")
            text_color = QColor("#ffffff")
        else:
            border_color = (
                QColor(self.model.border_color)
                if hasattr(self.model, "border_color")
                else default_border
            )
            text_color = (
                QColor(self.model.text_color)
                if hasattr(self.model, "text_color")
                else default_text
            )

        painter.setBrush(QBrush(fill_color))
        painter.setPen(QPen(border_color, 2))
        painter.drawEllipse(self.boundingRect())

        self.draw_multiline_text(painter, text_color)

        if self.isSelected():
            painter.setPen(QPen(Qt.GlobalColor.yellow, 3))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(self.boundingRect())

        if clipped:
            painter.restore()

    def get_serializable_properties(self):
        base_properties = super().get_serializable_properties()
        base_properties["content_offset_x"] = getattr(
            self.model, "content_offset_x", 0.0
        )
        base_properties["content_offset_y"] = getattr(
            self.model, "content_offset_y", 0.0
        )
        base_properties["position_in_subcanvas_x"] = getattr(
            self.model, "position_in_subcanvas_x", 0.0
        )
        base_properties["position_in_subcanvas_y"] = getattr(
            self.model, "position_in_subcanvas_y", 0.0
        )
        return base_properties

    def update_properties(self, properties: dict):
        super().update_properties(properties)
        self.update()
