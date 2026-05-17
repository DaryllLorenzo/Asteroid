# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------

# app/ui/components/dependency_item/why_link_edge_item.py
import math

from PyQt6.QtCore import QPointF
from PyQt6.QtCore import QRectF
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush
from PyQt6.QtGui import QColor
from PyQt6.QtGui import QFont
from PyQt6.QtGui import QFontMetrics
from PyQt6.QtGui import QPainter
from PyQt6.QtGui import QPolygonF
from PyQt6.QtWidgets import QStyleOptionGraphicsItem
from PyQt6.QtWidgets import QWidget

from app.i18n import tr
from app.ui.components.base_edge_item import BaseEdgeItem


class WhyLinkArrowItem(BaseEdgeItem):
    """
    Why Link Arrow Item.

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
        extra = 20  # suficiente for triángulo + text
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
        painter.drawPath(path)

        # Triángulo y text "WHY" in the punto MIDDLE REAL of the path curvo
        # Usamos the method utilitario for get the punto y ángulo correctos
        mid_point, mid_angle = self._get_point_at_percentage(0.5)

        # Ángulo of the path in the punto middle
        angle = mid_angle
        size = 12.0

        # Dibujamos triángulo relleno apuntando in the dirección of the path
        p_tip = mid_point
        p1 = QPointF(
            p_tip.x() - size * math.cos(angle - math.pi / 6),
            p_tip.y() - size * math.sin(angle - math.pi / 6),
        )
        p2 = QPointF(
            p_tip.x() - size * math.cos(angle + math.pi / 6),
            p_tip.y() - size * math.sin(angle + math.pi / 6),
        )

        painter.setBrush(QBrush(self.pen().color()))
        painter.drawPolygon(QPolygonF([p_tip, p1, p2]))

        # Text "WHY" centrado above of the flecha
        # Rotado for alinearse with the path
        font = QFont("Arial", 9)
        font.setBold(True)
        painter.setFont(font)
        fm = QFontMetrics(font)
        txt = tr("WHY")
        w = fm.horizontalAdvance(txt)
        h = fm.height()

        # Desplazamiento vertical for that no choque with the triángulo
        # Usamos coordinates rotadas for alinear with the path
        painter.save()
        painter.translate(mid_point)
        painter.rotate(math.degrees(angle))

        # The text itself dibuja perpendicularmente top of the path
        text_offset = size + 2
        text_rect = QRectF(-w / 2, -text_offset - h / 2, w, h)
        painter.setPen(self.pen().color())
        painter.drawText(text_rect, int(Qt.AlignmentFlag.AlignCenter), txt)
        painter.restore()

        if clipped:
            painter.restore()
