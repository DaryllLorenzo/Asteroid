# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------

# app/ui/components/dependency_item/or_decomposition_edge_item.py
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


class OrDecompositionArrowItem(BaseEdgeItem):
    """
    Or Decomposition Arrow Item.

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
        # Extra for the cabeza of flecha (triángulo of ~12px)
        extra = 15
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

        # Size of the cabeza of flecha
        size = 12.0

        # Calculate ángulo usando the LAST segmento real of the path curvo
        end_point = self._end_point

        # Determinar the last segmento for calculate the ángulo correcto
        if self.control_points:
            last_point = self.control_points[-1]
        else:
            last_point = self._start_point

        dx = end_point.x() - last_point.x()
        dy = end_point.y() - last_point.y()

        if dx == 0 and dy == 0:
            return

        angle = math.atan2(dy, dx)

        # Calculate the punto donde termina the line (base of the triángulo)
        line_end_point = QPointF(
            end_point.x() - size * math.cos(angle),
            end_point.y() - size * math.sin(angle),
        )

        # Create a path modificado that termine in the base of the triángulo
        # Get todos the puntos of the path original (already in coordinates local)
        path_points, start_point, _ = self._calculate_path_points()

        if len(path_points) >= 2:
            # If there is control points, the last segmento va of the last control point
            # al end_point. Reemplazamos the last punto with line_end_point
            if self.control_points:
                modified_points = path_points[:-1] + [line_end_point]
            else:
                modified_points = [start_point, line_end_point]

            # The puntos already están in coordinates local
            modified_path = QPainterPath(modified_points[0])
            for point in modified_points[1:]:
                modified_path.lineTo(point)

            # Dibujar the path modificado (line that termina before)
            painter.drawPath(modified_path)
        else:
            # Fallback: dibujar path original
            painter.drawPath(path)

        # Dibujar triángulo without relleno in the punta
        perp_x = math.sin(angle) * (size * 0.5)
        perp_y = -math.cos(angle) * (size * 0.5)

        p_tip = end_point
        p_base = line_end_point

        p1 = QPointF(p_base.x() + perp_x, p_base.y() + perp_y)
        p2 = QPointF(p_base.x() - perp_x, p_base.y() - perp_y)

        poly = QPolygonF([p_tip, p1, p2])
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPolygon(poly)

        if clipped:
            painter.restore()
