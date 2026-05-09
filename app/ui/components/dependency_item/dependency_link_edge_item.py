# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
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
    """Flecha tipo dependency: línea de centro a centro con triángulo en el medio."""

    def __init__(self, source_node, dest_node):
        super().__init__(source_node, dest_node, color=QColor(0, 0, 0), dashed=False)

    def boundingRect(self):
        """Extiende el bounding rect para incluir el triángulo en medio de la línea."""
        extra = 15  # suficiente para el triángulo
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

        # NO llamar a update_position() aquí para evitar temblor
        path = self.path()
        if path.isEmpty():
            if clipped:
                painter.restore()
            return

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(self.pen())

        # Dibujar la ruta (línea con control points si existen)
        painter.drawPath(path)

        # Triángulo en el punto MEDIO REAL del path curvo
        # Usamos el método utilitario para obtener el punto y ángulo correctos
        mid_point, mid_angle = self._get_point_at_percentage(0.5)

        # Dibujar triángulo apuntando en la dirección del path
        size = 12.0
        # El vértice del triángulo apunta en la dirección del path
        p_tip = mid_point
        # Los otros dos vértices forman la base del triángulo

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
