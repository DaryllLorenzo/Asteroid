# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------

import math

from PyQt6.QtCore import QPointF
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush
from PyQt6.QtGui import QColor
from PyQt6.QtGui import QPen
from PyQt6.QtGui import QPolygonF

from app.core.models.tropos_element.plan import Plan
from app.ui.components.base_tropos_item import BaseTroposItem
from app.ui.theme_manager import theme_manager


class PlanNodeItem(BaseTroposItem):
    """
    Plan Node Item.

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
        super().__init__(Plan(x, y, radius))

    def _get_distance_to_border(self, pos: QPointF) -> float:
        #  Usar _independent_model si existe
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
        points = [
            QPointF(-r, 0),
            QPointF(-r / 2, -r / 2),
            QPointF(r / 2, -r / 2),
            QPointF(r, 0),
            QPointF(r / 2, r / 2),
            QPointF(-r / 2, r / 2),
        ]
        min_dist = float("inf")
        n = len(points)
        for i in range(n):
            p1 = points[i]
            p2 = points[(i + 1) % n]
            dist = self._point_to_segment_distance(pos, p1, p2)
            min_dist = min(min_dist, dist)
        return min_dist

    def _point_to_segment_distance(
        self,
        p: QPointF,
        a: QPointF,
        b: QPointF,
    ) -> float:
        """
        Point To Segment Distance.

        Args:
            p (QPointF): The p.
            a (QPointF): The a.
            b (QPointF): The b.

        Returns:
            float: Point To Segment Distance.
        """
        ap = QPointF(p.x() - a.x(), p.y() - a.y())
        ab = QPointF(b.x() - a.x(), b.y() - a.y())
        ab2 = ab.x() * ab.x() + ab.y() * ab.y()
        if ab2 == 0:
            return math.sqrt(ap.x() * ap.x() + ap.y() * ap.y())
        t = (ap.x() * ab.x() + ap.y() * ab.y()) / ab2
        t = max(0, min(1, t))
        projection = QPointF(a.x() + t * ab.x(), a.y() + t * ab.y())
        dx = p.x() - projection.x()
        dy = p.y() - projection.y()
        return math.sqrt(dx * dx + dy * dy)

    def _get_new_radius_from_pos(self, pos: QPointF) -> float:
        """
        Get New Radius From Pos.

        Args:
            pos (QPointF): The pos.

        Returns:
            float: Get New Radius From Pos.
        """
        return float(max((pos.x() ** 2 + pos.y() ** 2) ** 0.5, 15.0))

    def paint(self, painter, option, widget=None):
        """
        Paint.

        Args:
            painter: The painter.
            option: The option.
            widget: The widget.
        """
        clipped = self.apply_subcanvas_clipping(painter)

        default_color = QColor(150, 180, 250)
        default_border = QColor(0, 0, 0)
        default_text = QColor(255, 255, 255)

        #  Usar _independent_model if existe (for nodes composite internos)
        model_for_props = (
            self._independent_model
            if hasattr(self, "_independent_model") and self._independent_model
            else self.model
        )

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

        painter.setBrush(QBrush(fill_color))
        painter.setPen(QPen(border_color, 2))

        #  Usar radius of the model independiente
        r = model_for_props.radius
        points = [
            QPointF(-r, 0),
            QPointF(-r / 2, -r / 2),
            QPointF(r / 2, -r / 2),
            QPointF(r, 0),
            QPointF(r / 2, r / 2),
            QPointF(-r / 2, r / 2),
        ]
        painter.drawPolygon(QPolygonF(points))

        #   DIBUJAR TEXT MULTILÍNEA
        self.draw_multiline_text(painter, text_color)

        if self.isSelected():
            painter.setPen(QPen(Qt.GlobalColor.yellow, 3))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPolygon(QPolygonF(points))

        if clipped:
            painter.restore()

    def get_serializable_properties(self):
        """Get Serializable Properties."""
        base_properties = super().get_serializable_properties()
        base_properties["node_type"] = "plan"
        return base_properties

    def update_properties(self, properties: dict):
        """
        Update Properties.

        Args:
            properties (dict): The properties.
        """
        super().update_properties(properties)
