# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------

import logging
import math

from PyQt6.QtCore import QPointF
from PyQt6.QtCore import QRectF
from PyQt6.QtCore import Qt
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QBrush
from PyQt6.QtGui import QColor
from PyQt6.QtGui import QPainterPath
from PyQt6.QtGui import QPen
from PyQt6.QtWidgets import QGraphicsObject
from PyQt6.QtWidgets import QGraphicsRectItem

from app.ui.theme_manager import theme_manager

logger = logging.getLogger(__name__)

# List of tipos of "links" soportados inside of the subcanvas
ARROW_TYPES = {
    "dependency_link",
    "why_link",
    "or_decomposition",
    "and_decomposition",
    "contribution",
    "means_end",
}


class ResizeHandle(QGraphicsRectItem):
    """The draggable handle for resizing a SubCanvasItem."""

    def __init__(self, parent_subcanvas, size: float = 10.0):
        super().__init__(-size / 2.0, -size / 2.0, size, size)
        self.setParentItem(parent_subcanvas)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable, False)
        self.setAcceptHoverEvents(True)
        self.parent_subcanvas = parent_subcanvas
        self.setCursor(Qt.CursorShape.SizeAllCursor)

    def mouseMoveEvent(self, event):
        local_scene = event.scenePos()
        center_scene = self.parent_subcanvas.mapToScene(QPointF(0.0, 0.0))
        dx = local_scene.x() - center_scene.x()
        dy = local_scene.y() - center_scene.y()
        new_r = max(20.0, math.hypot(dx, dy))
        self.parent_subcanvas.set_radius(new_r)
        event.accept()


class SubCanvasItem(QGraphicsObject):
    """The circular inner canvas hosted inside an Actor/Agent node."""

    subnode_dropped = pyqtSignal(str, float, float)  # item_type, local_x, local_y
    subarrow_dropped = pyqtSignal(str)  # arrow_type

    def __init__(self, radius: float = 80.0, parent=None):
        super().__init__(parent)
        self.radius = float(radius)
        self.original_radius = float(radius)

        # Not independently movable - it follows its parent node.
        self.setFlag(QGraphicsObject.GraphicsItemFlag.ItemIsMovable, False)
        self.setFlag(QGraphicsObject.GraphicsItemFlag.ItemIsSelectable, False)
        self.setAcceptDrops(True)

        self.border_pen = QPen(Qt.GlobalColor.black, 2)
        self.bg_brush = QBrush(Qt.GlobalColor.white)

        # The handle is a child item, not added to the scene separately.
        self.handle = ResizeHandle(self, size=10)
        self._update_handle_pos()

    def boundingRect(self) -> QRectF:
        r = float(self.radius)
        margin = 4.0
        return QRectF(
            -r - margin, -r - margin, 2.0 * r + margin * 2.0, 2.0 * r + margin * 2.0
        )

    def shape(self):
        path = QPainterPath()
        r = float(self.radius)
        path.addEllipse(QRectF(-r, -r, 2.0 * r, 2.0 * r))
        return path

    def paint(self, painter, option, widget=None):
        painter.save()

        r = float(self.radius)

        clip_path = QPainterPath()
        clip_path.addEllipse(QRectF(-r, -r, 2.0 * r, 2.0 * r))

        # Clipping SOLO visual
        painter.setClipPath(clip_path)

        colors = theme_manager().current
        border_pen = QPen(QColor(colors.subcanvas_border), 2)
        bg_brush = QBrush(QColor(colors.subcanvas_fill))

        painter.setBrush(bg_brush)
        painter.setOpacity(0.04)
        painter.setPen(Qt.PenStyle.NoPen)

        painter.drawEllipse(QRectF(-r, -r, 2.0 * r, 2.0 * r))

        painter.restore()

        # Border is drawn outside the clip, so it isn't dimmed by the fill.
        painter.setPen(border_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        painter.drawEllipse(QRectF(-r, -r, 2.0 * r, 2.0 * r))

    def set_radius(self, new_r: float):
        self.prepareGeometryChange()
        self.radius = max(20.0, float(new_r))
        self._update_handle_pos()
        self.update()

    def _update_handle_pos(self):
        if hasattr(self, "handle") and self.handle is not None:
            self.handle.setPos(self.radius, 0.0)

    # The subcanvas ignores mouse events so they fall through to the
    # parent node (e.g. dragging the node itself still works).
    def mousePressEvent(self, event):
        event.ignore()

    def mouseDoubleClickEvent(self, event):
        event.ignore()

    def reset_to_original_size(self):
        self.set_radius(self.original_radius)

    # -------------------------
    # Drag & Drop
    # -------------------------
    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if not event.mimeData().hasText():
            event.ignore()
            return

        item_type = event.mimeData().text()
        pos = event.pos()

        if item_type in ARROW_TYPES:
            logger.debug("Arrow dropped '%s' (local %s)", item_type, pos)
            self.subarrow_dropped.emit(item_type)
            event.acceptProposedAction()
            return

        # If no es flecha, lo tratamos as node tropos
        logger.debug(
            "Node dropped '%s' at local (%.1f, %.1f)", item_type, pos.x(), pos.y()
        )
        self.subnode_dropped.emit(item_type, float(pos.x()), float(pos.y()))
        event.acceptProposedAction()
