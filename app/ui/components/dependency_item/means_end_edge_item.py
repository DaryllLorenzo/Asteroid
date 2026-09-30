# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------

import math

from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QPainter
from PyQt6.QtGui import QPen
from PyQt6.QtWidgets import QStyleOptionGraphicsItem
from PyQt6.QtWidgets import QWidget

from app.ui.components.base_edge_item import BaseEdgeItem


class MeansEndArrowItem(BaseEdgeItem):
    """Arrow with an open V head."""

    def __init__(self, source_node, dest_node):
        super().__init__(source_node, dest_node, color=QPen().color(), dashed=False)

    def boundingRect(self):
        base_rect = super().boundingRect()
        extra = 15  # room for the open V head
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
        painter.drawPath(path)

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
        ux = math.cos(angle)
        uy = math.sin(angle)
        perp_x = -uy
        perp_y = ux

        size = 12.0

        pA = QPointF(
            end_point.x() - ux * size + perp_x * (size * 0.4),
            end_point.y() - uy * size + perp_y * (size * 0.4),
        )
        pB = QPointF(
            end_point.x() - ux * size - perp_x * (size * 0.4),
            end_point.y() - uy * size - perp_y * (size * 0.4),
        )
        painter.drawLine(end_point, pA)
        painter.drawLine(end_point, pB)

        if clipped:
            painter.restore()
