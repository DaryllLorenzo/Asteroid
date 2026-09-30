# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------

import math

from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QBrush
from PyQt6.QtGui import QColor
from PyQt6.QtGui import QPainter
from PyQt6.QtGui import QPolygonF
from PyQt6.QtWidgets import QStyleOptionGraphicsItem
from PyQt6.QtWidgets import QWidget

from app.ui.components.base_edge_item import BaseEdgeItem


class DependencyLinkArrowItem(BaseEdgeItem):
    """Arrow with a filled triangle at the path's midpoint."""

    def __init__(self, source_node, dest_node):
        super().__init__(source_node, dest_node, color=QColor(0, 0, 0), dashed=False)

    def boundingRect(self):
        extra = 15  # room for the triangle
        return super().boundingRect().adjusted(-extra, -extra, extra, extra)

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

        # Triangle at the true midpoint of the (possibly curved) path.
        mid_point, mid_angle = self._get_point_at_percentage(0.5)

        size = 12.0
        p_tip = mid_point

        p1 = QPointF(
            p_tip.x() - size * math.cos(mid_angle - math.pi / 6),
            p_tip.y() - size * math.sin(mid_angle - math.pi / 6),
        )
        p2 = QPointF(
            p_tip.x() - size * math.cos(mid_angle + math.pi / 6),
            p_tip.y() - size * math.sin(mid_angle + math.pi / 6),
        )

        poly = QPolygonF([p_tip, p1, p2])
        painter.setBrush(QBrush(self.pen().color()))
        painter.drawPolygon(poly)

        if clipped:
            painter.restore()
