# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------
import math

from PyQt6.QtCore import QPointF
from PyQt6.QtCore import QRectF
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush
from PyQt6.QtGui import QColor
from PyQt6.QtGui import QPainterPath
from PyQt6.QtGui import QPen

from app.core.models.tropos_element.hard_goal import HardGoal
from app.ui.components.base_tropos_item import BaseTroposItem


class HardGoalNodeItem(BaseTroposItem):
    """
    Hard Goal Node Item.

    Methods:
        __init__: Initialize the instance.
        paint: Paint.
        get_serializable_properties: Get Serializable Properties.
        update_properties: Update Properties.
    """

    def __init__(self, x=0, y=0, radius=60):
        """
        Initialize the instance.

        Args:
            x: The x.
            y: The y.
            radius: The radius.
        """
        super().__init__(HardGoal(x, y, radius))

    def _get_distance_to_border(self, pos: QPointF) -> float:
        # Usar _independent_model si existe
        """
        Get Distance To Border.

        Args:
            pos (QPointF): The pos.

        Returns:
            float: Get Distance To Border.
        """
        model_for_props = (
            self._independent_model
            if hasattr(self, "_independent_model") and self._independent_model
            else self.model
        )
        r = model_for_props.radius
        rect = QRectF(-r, -r / 2, 2 * r, r)
        if rect.contains(pos):
            dist_left = abs(pos.x() - rect.left())
            dist_right = abs(pos.x() - rect.right())
            dist_top = abs(pos.y() - rect.top())
            dist_bottom = abs(pos.y() - rect.bottom())
            return float(min(dist_left, dist_right, dist_top, dist_bottom))
        else:
            dx = max(rect.left() - pos.x(), 0, pos.x() - rect.right())
            dy = max(rect.top() - pos.y(), 0, pos.y() - rect.bottom())
            return float(math.sqrt(dx * dx + dy * dy))

    def _get_new_radius_from_pos(self, pos: QPointF) -> float:
        """
        Get New Radius From Pos.

        Args:
            pos (QPointF): The pos.

        Returns:
            float: Get New Radius From Pos.
        """
        new_r = abs(pos.x())
        return float(max(new_r, 20.0))

    def paint(self, painter, option, widget=None):
        """
        Paint.

        Args:
            painter: The painter.
            option: The option.
            widget: The widget.
        """
        clipped = self.apply_subcanvas_clipping(painter)

        default_color = QColor(150, 200, 150)
        default_border = QColor(0, 0, 0)
        default_text = QColor(255, 255, 255)

        # Usar _independent_model if existe (for nodes composite internos)
        model_for_props = (
            self._independent_model
            if hasattr(self, "_independent_model") and self._independent_model
            else self.model
        )

        # Colores son sincronizados, usar self.model (wrapper)
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

        painter.setRenderHint(painter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(fill_color))
        painter.setPen(QPen(border_color, 2))

        # Usar radius of the model independiente
        r = model_for_props.radius
        rect = QRectF(-r, -r / 2, 2 * r, r)
        path = QPainterPath()
        path.addRoundedRect(rect, r / 2, r / 2)
        painter.drawPath(path)

        #   DIBUJAR TEXT MULTILÍNEA
        self.draw_multiline_text(painter, text_color)

        if self.isSelected():
            painter.setPen(QPen(Qt.GlobalColor.yellow, 3))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(path)

        if clipped:
            painter.restore()

    def get_serializable_properties(self):
        """Get Serializable Properties."""
        base_properties = super().get_serializable_properties()
        base_properties["node_type"] = "hard_goal"
        return base_properties

    def update_properties(self, properties: dict):
        """
        Update Properties.

        Args:
            properties (dict): The properties.
        """
        super().update_properties(properties)
