# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------

# app/ui/components/dependency_item/dependency_link_edge_item.py
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
    """
    Dependency Link Arrow Item.

    Methods:
        __init__: Initialize the instance.
        boundingRect: Boundingrect.
        paint: Paint.
    """

    def __init__(self, source_node, dest_node):
        """
        Initialize the instance.

        Args:
            source_node: The source node.
            dest_node: The dest node.
        """
        super().__init__(source_node, dest_node, color=QColor(0, 0, 0), dashed=False)

    def boundingRect(self):
        """Boundingrect."""
        extra = 15  # suficiente for the triángulo
        return super().boundingRect().adjusted(-extra, -extra, extra, extra)

    def paint(
        self,
        painter: QPainter | None,
        option: QStyleOptionGraphicsItem | None,
        widget: QWidget | None = None,
    ) -> None:
        """
        Paint.

        Args:
            painter (QPainter | None): The painter.
            option (QStyleOptionGraphicsItem | None): The option.
            widget (QWidget | None): The widget.
        """
        if painter is None:
            return
        del option, widget

        clipped = self.apply_subcanvas_clipping(painter)

        if painter is None or not self.source_node or not self.dest_node:
            if clipped:
                painter.restore()
            return

        # NO llamar a update_position() here for avoid temblor
        path = self.path()
        if path.isEmpty():
            if clipped:
                painter.restore()
            return

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(self.pen())

        # Dibujar the path (line with control points if existen)
        painter.drawPath(path)

        # Triángulo in the punto MIDDLE REAL of the path curvo
        # Usamos the method utilitario for get the punto y ángulo correctos
        mid_point, mid_angle = self._get_point_at_percentage(0.5)

        # Dibujar triángulo apuntando in the dirección of the path
        size = 12.0
        # The vértice of the triángulo apunta in the dirección of the path
        p_tip = mid_point
        # The otros dos vértices forman the base of the triángulo

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
