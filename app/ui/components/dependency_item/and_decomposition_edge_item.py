# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------

import math

from PyQt6.QtCore import QPointF
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter
from PyQt6.QtGui import QPainterPath
from PyQt6.QtGui import QPen
from PyQt6.QtGui import QPolygonF
from PyQt6.QtWidgets import QStyleOptionGraphicsItem
from PyQt6.QtWidgets import QWidget

from app.ui.components.base_edge_item import BaseEdgeItem


class AndDecompositionArrowItem(BaseEdgeItem):
    """Arrow with an open triangular head and a perpendicular T-bar at 60%."""

    def __init__(self, source_node, dest_node):
        super().__init__(source_node, dest_node, color=QPen().color(), dashed=False)

    def boundingRect(self):
        base_rect = super().boundingRect()
        extra = 20  # room for the arrow head and the T-bar
        return base_rect.adjusted(-extra, -extra, extra, extra)

    def paint(
        self,
        painter: QPainter | None,
        option: QStyleOptionGraphicsItem | None,
        widget: QWidget | None = None,
    ) -> None:
        if painter is None:
            return
        del option, widget

        clipped = self.apply_subcanvas_clipping(painter)

        if painter is None or not self.source_node or not self.dest_node:
            if clipped:
                painter.restore()
            return

        # Don't call update_position() here - it would jitter while dragging.
        path = self.path()
        if path.isEmpty():
            if clipped:
                painter.restore()
            return

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(self.pen())

        arrow_size = 12.0

        end_point = self._end_point

        if self.control_points:
            last_point = self.control_points[-1]
        else:
            last_point = self._start_point

        dx = end_point.x() - last_point.x()
        dy = end_point.y() - last_point.y()

        if dx == 0 and dy == 0:
            return

        angle = math.atan2(dy, dx)
        perp_x = -math.sin(angle)
        perp_y = math.cos(angle)

        # Where the line stops short, to leave room for the triangle head.
        line_end_point = QPointF(
            end_point.x() - arrow_size * math.cos(angle),
            end_point.y() - arrow_size * math.sin(angle),
        )

        path_points, start_point, _ = self._calculate_path_points()

        if len(path_points) >= 2:
            if self.control_points:
                modified_points = path_points[:-1] + [line_end_point]
            else:
                modified_points = [start_point, line_end_point]

            modified_path = QPainterPath(modified_points[0])
            for point in modified_points[1:]:
                modified_path.lineTo(point)

            painter.drawPath(modified_path)
        else:
            painter.drawPath(path)

        # Open (unfilled) triangular head.
        p_tip = end_point
        base = line_end_point

        corner1 = QPointF(
            base.x() + perp_x * (0.5 * arrow_size),
            base.y() + perp_y * (0.5 * arrow_size),
        )
        corner2 = QPointF(
            base.x() - perp_x * (0.5 * arrow_size),
            base.y() - perp_y * (0.5 * arrow_size),
        )

        poly = QPolygonF([p_tip, corner1, corner2])
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPolygon(poly)

        # T-bar at the true 60% point along the (possibly curved) path.
        bar_point, bar_angle = self._get_point_at_percentage(0.6)

        half = 6.0
        bar_perp_x = -math.sin(bar_angle)
        bar_perp_y = math.cos(bar_angle)

        pa = QPointF(
            bar_point.x() - bar_perp_x * half, bar_point.y() - bar_perp_y * half
        )
        pb = QPointF(
            bar_point.x() + bar_perp_x * half, bar_point.y() + bar_perp_y * half
        )
        painter.drawLine(pa, pb)

        if clipped:
            painter.restore()
