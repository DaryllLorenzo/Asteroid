# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------

from PyQt6.QtCore import QPointF
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush
from PyQt6.QtGui import QColor
from PyQt6.QtGui import QPen

from app.core.models.entity.agent import Agent
from app.ui.components.base_node_item import BaseNodeItem


class AgentNodeItem(BaseNodeItem):
    """
    Agent Node Item.

    Methods:
        __init__: Initialize the instance.
        paint: Paint.
        get_serializable_properties: Get Serializable Properties.
        update_properties: Update Properties.
    """

    def __init__(self, x=0, y=0, radius=50):
        """
        Initialize the instance.

        Args:
            x: The x.
            y: The y.
            radius: The radius.
        """
        super().__init__(Agent(x, y, radius))

    def _get_distance_to_border(self, pos: QPointF) -> float:
        """
        Get Distance To Border.

        Args:
            pos (QPointF): The pos.

        Returns:
            float: Get Distance To Border.
        """
        r = float(self.model.radius)
        center_dist = (pos.x() ** 2 + pos.y() ** 2) ** 0.5
        return float(abs(center_dist - r))

    def paint(self, painter, option, widget=None):
        # Apply clipping if node internal of subcanvas
        """
        Paint.

        Args:
            painter: The painter.
            option: The option.
            widget: The widget.
        """
        clipped = self.apply_subcanvas_clipping(painter)

        # 1. Colors
        default_color = QColor(250, 150, 100)
        default_border = QColor(0, 0, 0)
        default_text = QColor(255, 255, 255)

        fill_color = (
            QColor(self.model.color) if hasattr(self.model, "color") else default_color
        )
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

        # 2. Draw THE CONTAINER
        painter.setBrush(QBrush(fill_color))
        painter.setPen(QPen(border_color, 2))
        painter.drawEllipse(self.boundingRect())

        # 3. Draw TEXT (Multilínea)
        self.draw_multiline_text(painter, text_color)

        # 4. Draw THE LINE OF THE AGENTE
        # The line must move with the offset like the text.
        content_off_x = getattr(self.model, "content_offset_x", 0.0)
        content_off_y = getattr(self.model, "content_offset_y", 0.0)

        painter.save()
        # Apply offset only for the line (the text already itself drew in its place)
        painter.translate(content_off_x, content_off_y)

        y_position = int(-self.model.radius * 0.3)
        painter.setPen(QPen(border_color, 2))
        painter.drawLine(
            int(-self.model.radius), y_position, int(self.model.radius), y_position
        )
        painter.restore()

        # 5. Indicador of selection
        if self.isSelected():
            painter.setPen(QPen(Qt.GlobalColor.yellow, 3))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(self.boundingRect())

        if clipped:
            painter.restore()

    def get_serializable_properties(self):
        """Get Serializable Properties."""
        base_properties = super().get_serializable_properties()
        base_properties["node_type"] = "agent"
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
        """
        Update Properties.

        Args:
            properties (dict): The properties.
        """
        super().update_properties(properties)
        self.update()
