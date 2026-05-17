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

from app.core.models.tropos_element.soft_goal import SoftGoal
from app.ui.components.base_tropos_item import BaseTroposItem
from app.ui.theme_manager import theme_manager


class SoftGoalNodeItem(BaseTroposItem):
    """
    Soft Goal Node Item.

    Methods:
        __init__: Initialize the instance.
        boundingRect: Boundingrect.
        set_radius: Set Radius.
        paint: Paint.
        get_serializable_properties: Get Serializable Properties.
        update_properties: Update Properties.
    """

    def __init__(self, x=0, y=0, radius=30):
        """
        Initialize the instance.

        Args:
            x: The x.
            y: The y.
            radius: The radius.
        """
        super().__init__(SoftGoal(x, y, radius))
        self.model.radius = radius
        self.path: QPainterPath = self._create_cloud_path()

    def _create_cloud_path(self) -> QPainterPath:
        """
        Create Cloud Path.

        Returns:
            QPainterPath: Create Cloud Path.
        """
        return self._create_cloud_path_for_radius(float(self.model.radius))

    def _create_cloud_path_for_radius(self, r: float) -> QPainterPath:
        """
        Create Cloud Path For Radius.

        Args:
            r (float): The r.

        Returns:
            QPainterPath: Create Cloud Path For Radius.
        """
        path = QPainterPath()
        w = r * 2.8
        h = r * 0.95

        path.moveTo(-w * 0.85, 0)
        path.cubicTo(-w * 1.05, -h * 0.8, -w * 0.75, -h * 1.3, -w * 0.35, -h * 0.85)
        path.cubicTo(-w * 0.15, -h * 1.25, w * 0.15, -h * 1.25, w * 0.35, -h * 0.85)
        path.cubicTo(w * 0.75, -h * 1.3, w * 1.05, -h * 0.8, w * 0.85, 0)
        path.cubicTo(w * 1.05, h * 0.8, w * 0.75, h * 1.3, w * 0.35, h * 0.85)
        path.cubicTo(w * 0.15, h * 1.25, -w * 0.15, h * 1.25, -w * 0.35, h * 0.85)
        path.cubicTo(-w * 0.75, h * 1.3, -w * 1.05, h * 0.8, -w * 0.85, 0)
        path.closeSubpath()
        return path

    def boundingRect(self) -> QRectF:
        # Use _independent_model if it exists (for internal composite nodes)
        """
        Boundingrect.

        Returns:
            QRectF: Boundingrect.
        """
        model_for_props = (
            self._independent_model
            if hasattr(self, "_independent_model") and self._independent_model
            else self.model
        )
        r = float(model_for_props.radius)
        if not hasattr(self, "path") or self.path.isEmpty():
            return QRectF(-r, -r, r * 2, r * 2)
        return self.path.boundingRect().adjusted(-2, -2, 2, 2)

    def _get_distance_to_border(self, pos: QPointF) -> float:
        """
        Get Distance To Border.

        Args:
            pos (QPointF): The pos.

        Returns:
            float: Get Distance To Border.
        """
        # Use _independent_model if it exists
        model_for_props = (
            self._independent_model
            if hasattr(self, "_independent_model") and self._independent_model
            else self.model
        )

        if hasattr(self, "path") and not self.path.isEmpty():
            # Create a stroker for simular the border
            from PyQt6.QtGui import QPainterPathStroker

            stroker = QPainterPathStroker()
            stroker.setWidth(10)  # Ancho of the área of detección

            # Create path for the border
            stroke_path = stroker.createStroke(self.path)

            # If the punto this in the border, distancia = 0
            if stroke_path.contains(pos):
                return 0
            else:
                # Calculate distancia al bounding rect as aproximación
                br = self.path.boundingRect()
                center = br.center()
                dist_to_center = math.sqrt(
                    (pos.x() - center.x()) ** 2 + (pos.y() - center.y()) ** 2
                )
                # Aproximación simple
                return abs(dist_to_center - float(model_for_props.radius))
        return super()._get_distance_to_border(pos)

    def _get_new_radius_from_pos(self, pos: QPointF) -> float:
        """
        Get New Radius From Pos.

        Args:
            pos (QPointF): The pos.

        Returns:
            float: Get New Radius From Pos.
        """
        return float(max((pos.x() ** 2 + pos.y() ** 2) ** 0.5, 15.0))

    def set_radius(self, new_r: float) -> None:
        """
        Set Radius.

        Args:
            new_r (float): The new r.
        """
        self.prepareGeometryChange()
        old_r = (
            self._independent_model.radius
            if self._independent_model
            else self.model.radius
        )

        # Use the independent model if available
        if self._independent_model:
            self._independent_model.radius = new_r
        else:
            self.model.radius = new_r

        # Recreate the path with the new radius
        r = (
            self._independent_model.radius
            if self._independent_model
            else self.model.radius
        )
        self.path = self._create_cloud_path_for_radius(r)

        self.update()

        if old_r != new_r:
            self.properties_changed.emit(self, {"radius": new_r})

    def paint(self, painter, option, widget=None):
        """
        Paint.

        Args:
            painter: The painter.
            option: The option.
            widget: The widget.
        """
        clipped = self.apply_subcanvas_clipping(painter)

        default_color = QColor(220, 220, 180)
        default_border = QColor(0, 0, 0)
        default_text = QColor(0, 0, 0)

        # Colores son sincronizados, usar self.model (wrapper)
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

        painter.setRenderHint(painter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(fill_color))
        painter.setPen(QPen(border_color, 2))

        # Draw the cloud using the current path
        painter.drawPath(self.path)

        # DIBUJAR TEXT MULTILÍNEA
        # The text itself dibujará centrado over the nube
        self.draw_multiline_text(painter, text_color)

        if self.isSelected():
            painter.setPen(QPen(Qt.GlobalColor.yellow, 3))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(self.path)

        if clipped:
            painter.restore()

    def get_serializable_properties(self):
        """Get Serializable Properties."""
        base_properties = super().get_serializable_properties()
        base_properties["node_type"] = "soft_goal"
        return base_properties

    def update_properties(self, properties: dict):
        """
        Update Properties.

        Args:
            properties (dict): The properties.
        """
        super().update_properties(properties)
