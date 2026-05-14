# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------

# app/ui/components/dependency_item/contribution_edge_item.py
import math

from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QFont
from PyQt6.QtGui import QPainter
from PyQt6.QtGui import QPen
from PyQt6.QtWidgets import QStyleOptionGraphicsItem
from PyQt6.QtWidgets import QWidget

from app.ui.components.base_edge_item import BaseEdgeItem


class ContributionArrowItem(BaseEdgeItem):
    """
    Contribution Arrow Item.

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
        super().__init__(source_node, dest_node, color=QPen().color(), dashed=False)

    def boundingRect(self):
        """Boundingrect."""
        # Get boundingRect base of the line
        base_rect = super().boundingRect()
        # Extra for the V abierta (~12px) y the símbolo '+'
        extra = 20
        return base_rect.adjusted(-extra, -extra, extra, extra)

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

        # Get punto final y dirección for the punta of flecha
        end_point = self._end_point

        # Determinar the last segmento for dibujar the punta
        if self.control_points:
            last_point = self.control_points[-1]
        else:
            last_point = self._start_point

        # Calculate ángulo of the last segmento
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

        # V abierta (punta de flecha)
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

        # símbolo '+' in the punto middle REAL of the path curvo
        # Usamos the method utilitario for get the punto y ángulo correctos
        mid_point, mid_angle = self._get_point_at_percentage(0.5)

        painter.save()
        # Rotar the sistema of coordinates for alinear the '+' with the path
        painter.translate(mid_point)
        painter.rotate(math.degrees(mid_angle))

        painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        # Dibujar '+' centrado, ligeramente desplazado perpendicularmente
        # for no tapar the line
        fm = painter.fontMetrics()
        w = fm.horizontalAdvance("+")
        h = fm.height()
        # Small offset perpendicular for that the '+' no itself superponga with the line
        offset_perp = 8.0
        painter.drawText(QPointF(-w / 2, -h / 2 - offset_perp), "+")
        painter.restore()

        if clipped:
            painter.restore()
