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

from app.core.models.typed_node import TypedNode
from app.ui.components.base_tropos_item import BaseTroposItem
from app.ui.theme_manager import theme_manager


class PlanNodeItem(BaseTroposItem):
    def __init__(self, x=0, y=0, radius=50):
        super().__init__(TypedNode("plan", x, y, radius))

    def _get_distance_to_border(self, pos: QPointF) -> float:
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
        return float(max((pos.x() ** 2 + pos.y() ** 2) ** 0.5, 15.0))

    def paint(self, painter, option, widget=None):
        clipped = self.apply_subcanvas_clipping(painter)

        default_color = QColor(150, 180, 250)
        default_border = QColor(0, 0, 0)
        default_text = QColor(255, 255, 255)

        # Internal composite nodes may have their own radius, independent
        # of the shared (synced) model used for colors/label below.
        model_for_props = (
            self._independent_model
            if hasattr(self, "_independent_model") and self._independent_model
            else self.model
        )

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

        self.draw_multiline_text(painter, text_color)

        if self.isSelected():
            painter.setPen(QPen(Qt.GlobalColor.yellow, 3))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPolygon(QPolygonF(points))

        if clipped:
            painter.restore()

    def update_properties(self, properties: dict):
        super().update_properties(properties)
