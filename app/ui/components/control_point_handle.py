# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------

from collections.abc import Callable

from PyQt6.QtCore import QPointF
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush
from PyQt6.QtGui import QColor
from PyQt6.QtGui import QPen
from PyQt6.QtWidgets import QGraphicsEllipseItem
from PyQt6.QtWidgets import QGraphicsItem

from app.ui.theme_manager import theme_manager


class ControlPointHandle(QGraphicsEllipseItem):
    """A draggable handle for one control point on an edge."""

    HANDLE_SIZE = 10.0  # pixels

    def __init__(
        self,
        parent_edge,
        position: QPointF,
        on_position_changed: Callable | None = None,
        on_release: Callable | None = None,
        on_drag_start: Callable | None = None,
    ):
        super().__init__(
            -self.HANDLE_SIZE / 2,
            -self.HANDLE_SIZE / 2,
            self.HANDLE_SIZE,
            self.HANDLE_SIZE,
        )

        self.parent_edge = parent_edge
        self.on_position_changed = on_position_changed
        self.on_release = on_release
        self.on_drag_start = on_drag_start
        self.setPos(position)

        self._click_offset = QPointF(0, 0)

        colors = theme_manager().current
        self.setPen(QPen(QColor(colors.control_point_border), 2))
        self.setBrush(QBrush(QColor(colors.control_point_fill)))

        # Dragging is handled manually in mouseMoveEvent, not via
        # ItemIsMovable, so the parent edge can be notified of each move.
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        self.setAcceptHoverEvents(True)

        self.setCursor(Qt.CursorShape.SizeAllCursor)
        self.setZValue(100)  # above the edge line

        self._is_dragging = False

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = True
            self.setSelected(True)
            if self.on_drag_start:
                self.on_drag_start()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._is_dragging and event.buttons() & Qt.MouseButton.LeftButton:
            parent = self.parentItem()
            if parent:
                local_pos = parent.mapFromScene(event.scenePos())
                self.setPos(local_pos)
                new_pos = local_pos
            else:
                new_pos = event.scenePos()
                self.setPos(new_pos)

            if self.on_position_changed:
                self.on_position_changed(self, new_pos)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._is_dragging = False
        if self.on_release:
            self.on_release()
        super().mouseReleaseEvent(event)

    def hoverEnterEvent(self, event):
        colors = theme_manager().current
        self.setBrush(QBrush(QColor(colors.control_point_hover)))
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        if not self.isSelected():
            colors = theme_manager().current
            self.setBrush(QBrush(QColor(colors.control_point_fill)))
        super().hoverLeaveEvent(event)

    def update_appearance(self, is_selected: bool):
        colors = theme_manager().current
        if is_selected:
            self.setBrush(QBrush(QColor(colors.control_point_selected)))
        else:
            self.setBrush(QBrush(QColor(colors.control_point_fill)))
