# subcanvas_item.py (corregido)
# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------

import math

from PyQt6.QtCore import QPointF
from PyQt6.QtCore import QRectF
from PyQt6.QtCore import Qt
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QBrush
from PyQt6.QtGui import QPainterPath
from PyQt6.QtGui import QPen
from PyQt6.QtWidgets import QGraphicsObject
from PyQt6.QtWidgets import QGraphicsRectItem

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
    """
    Resize Handle.

    Methods:
        __init__: Initialize the instance.
        mouseMoveEvent: Mousemoveevent.
    """

    def __init__(self, parent_subcanvas, size: float = 10.0):
        """
        Initialize the instance.

        Args:
            parent_subcanvas: The parent subcanvas.
            size (float): The size.
        """
        super().__init__(-size / 2.0, -size / 2.0, size, size)
        self.setParentItem(parent_subcanvas)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable, False)
        self.setAcceptHoverEvents(True)
        self.parent_subcanvas = parent_subcanvas
        self.setCursor(Qt.CursorShape.SizeAllCursor)

    def mouseMoveEvent(self, event):
        """
        Mousemoveevent.

        Args:
            event: The event.
        """
        local_scene = event.scenePos()
        center_scene = self.parent_subcanvas.mapToScene(QPointF(0.0, 0.0))
        dx = local_scene.x() - center_scene.x()
        dy = local_scene.y() - center_scene.y()
        new_r = max(20.0, math.hypot(dx, dy))
        self.parent_subcanvas.set_radius(new_r)
        event.accept()


class SubCanvasItem(QGraphicsObject):
    # item_type, local_x, local_y  (nodes)
    """
    Sub Canvas Item.

    Methods:
        __init__: Initialize the instance.
        boundingRect: Boundingrect.
        shape: Shape.
        paint: Paint.
        set_radius: Set Radius.
        mousePressEvent: Mousepressevent.
        mouseDoubleClickEvent: Mousedoubleclickevent.
        reset_to_original_size: Reset To Original Size.
        dragEnterEvent: Dragenterevent.
        dragMoveEvent: Dragmoveevent.
        dropEvent: Dropevent.
    """

    subnode_dropped = pyqtSignal(str, float, float)
    # arrow_type (links)
    subarrow_dropped = pyqtSignal(str)

    def __init__(self, radius: float = 80.0, parent=None):
        """
        Initialize the instance.

        Args:
            radius (float): The radius.
            parent: The parent.
        """
        super().__init__(parent)
        self.radius = float(radius)
        self.original_radius = float(radius)

        # no movible by separado; itself moves with the node parent
        self.setFlag(QGraphicsObject.GraphicsItemFlag.ItemIsMovable, False)
        self.setFlag(QGraphicsObject.GraphicsItemFlag.ItemIsSelectable, False)
        self.setAcceptDrops(True)

        self.border_pen = QPen(Qt.GlobalColor.black, 2)
        self.bg_brush = QBrush(Qt.GlobalColor.white)

        # Create handle as child (no scene.addItem for the handle)
        self.handle = ResizeHandle(self, size=10)
        self._update_handle_pos()

    def boundingRect(self) -> QRectF:
        """
        Boundingrect.

        Returns:
            QRectF: Boundingrect.
        """
        r = float(self.radius)
        margin = 4.0
        return QRectF(
            -r - margin, -r - margin, 2.0 * r + margin * 2.0, 2.0 * r + margin * 2.0
        )

    def shape(self):
        """Shape."""
        path = QPainterPath()
        r = float(self.radius)
        path.addEllipse(QRectF(-r, -r, 2.0 * r, 2.0 * r))
        return path

    def paint(self, painter, option, widget=None):
        """
        Paint.

        Args:
            painter: The painter.
            option: The option.
            widget: The widget.
        """
        painter.save()

        r = float(self.radius)

        clip_path = QPainterPath()
        clip_path.addEllipse(QRectF(-r, -r, 2.0 * r, 2.0 * r))

        # Clipping SOLO visual
        painter.setClipPath(clip_path)

        painter.setBrush(self.bg_brush)
        painter.setOpacity(0.04)
        painter.setPen(Qt.PenStyle.NoPen)

        painter.drawEllipse(QRectF(-r, -r, 2.0 * r, 2.0 * r))

        painter.restore()

        # Dibujar border outside of the clipping
        painter.setPen(self.border_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        painter.drawEllipse(QRectF(-r, -r, 2.0 * r, 2.0 * r))

    def set_radius(self, new_r: float):
        """
        Set Radius.

        Args:
            new_r (float): The new r.
        """
        self.prepareGeometryChange()
        self.radius = max(20.0, float(new_r))
        self._update_handle_pos()
        self.update()

    def _update_handle_pos(self):
        """Update Handle Pos."""
        if hasattr(self, "handle") and self.handle is not None:
            self.handle.setPos(self.radius, 0.0)

    # MODIFICADO: Now the subcanvas NO acepta eventos of mouse,
    # for permitir that pasen al node parent
    def mousePressEvent(self, event):
        """
        Mousepressevent.

        Args:
            event: The event.
        """
        event.ignore()  # IMPORTANTE: Ignore for that llegue al node parent

    def mouseDoubleClickEvent(self, event):
        """
        Mousedoubleclickevent.

        Args:
            event: The event.
        """
        event.ignore()  # IMPORTANTE: Ignore for that llegue al node parent

    def reset_to_original_size(self):
        """Reset To Original Size."""
        self.set_radius(self.original_radius)

    # -------------------------
    # Drag & Drop (mantener funcionalidad)
    # -------------------------
    def dragEnterEvent(self, event):
        """
        Dragenterevent.

        Args:
            event: The event.
        """
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        """
        Dragmoveevent.

        Args:
            event: The event.
        """
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        """
        Dropevent.

        Args:
            event: The event.
        """
        if not event.mimeData().hasText():
            event.ignore()
            return

        item_type = event.mimeData().text()
        pos = event.pos()

        # If es a type of flecha (links new)
        if item_type in ARROW_TYPES:
            print(f"SubCanvasItem: arrow dropped '{item_type}' (local {pos})")
            self.subarrow_dropped.emit(item_type)
            event.acceptProposedAction()
            return

        # If no es flecha, lo tratamos as node tropos
        print(
            f"SubCanvasItem: node dropped '{item_type}' at "
            f"local ({pos.x():.1f}, {pos.y():.1f})"
        )
        self.subnode_dropped.emit(item_type, float(pos.x()), float(pos.y()))
        event.acceptProposedAction()
