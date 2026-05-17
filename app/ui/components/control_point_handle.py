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
    """
    Control Point Handle.

    Methods:
        __init__: Initialize the instance.
        mousePressEvent: Mousepressevent.
        mouseMoveEvent: Mousemoveevent.
        mouseReleaseEvent: Mousereleaseevent.
        hoverEnterEvent: Hoverenterevent.
        hoverLeaveEvent: Hoverleaveevent.
        update_appearance: Update Appearance.
    """

    HANDLE_SIZE = 10.0  # Size of the handle in píxeles

    def __init__(
        self,
        parent_edge,
        position: QPointF,
        on_position_changed: Callable | None = None,
        on_release: Callable | None = None,
        on_drag_start: Callable | None = None,
    ):
        """
        Initialize the instance.

        Args:
            parent_edge: The parent edge.
            position (QPointF): The position.
            on_position_changed (Callable | None): The on position changed.
            on_release (Callable | None): The on release.
            on_drag_start (Callable | None): The on drag start.
        """
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

        # Punto donde itself hizo click initial (for calculate offset)
        self._click_offset = QPointF(0, 0)

        # Configure apariencia
        colors = theme_manager().current
        self.setPen(QPen(QColor(colors.control_point_border), 2))
        self.setBrush(QBrush(QColor(colors.control_point_fill)))

        # NO usar ItemIsMovable - lo manejamos manualmente
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        self.setAcceptHoverEvents(True)

        # Cursor custom
        self.setCursor(Qt.CursorShape.SizeAllCursor)

        # Z-value alto for estar by above of the line
        self.setZValue(100)

        # State
        self._is_dragging = False

    def mousePressEvent(self, event):
        """
        Mousepressevent.

        Args:
            event: The event.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = True
            self.setSelected(True)
            if self.on_drag_start:
                self.on_drag_start()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """
        Mousemoveevent.

        Args:
            event: The event.
        """
        if self._is_dragging and event.buttons() & Qt.MouseButton.LeftButton:
            # Transform position of scene a coordinates local of the parent (edge)
            parent = self.parentItem()
            if parent:
                # Convert of coordinates of scene a coordinates local of the parent
                local_pos = parent.mapFromScene(event.scenePos())
                self.setPos(local_pos)
                new_pos = local_pos
            else:
                # Without parent, usar coordinates of scene directamente
                new_pos = event.scenePos()
                self.setPos(new_pos)

            # Notify al edge parent over the changed of position
            if self.on_position_changed:
                self.on_position_changed(self, new_pos)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """
        Mousereleaseevent.

        Args:
            event: The event.
        """
        self._is_dragging = False
        # Notify that itself dropped the handle
        if self.on_release:
            self.on_release()
        super().mouseReleaseEvent(event)

    def hoverEnterEvent(self, event):
        """
        Hoverenterevent.

        Args:
            event: The event.
        """
        colors = theme_manager().current
        self.setBrush(QBrush(QColor(colors.control_point_hover)))
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        """
        Hoverleaveevent.

        Args:
            event: The event.
        """
        if not self.isSelected():
            colors = theme_manager().current
            self.setBrush(QBrush(QColor(colors.control_point_fill)))
        super().hoverLeaveEvent(event)

    def update_appearance(self, is_selected: bool):
        """
        Update Appearance.

        Args:
            is_selected (bool): The is selected.
        """
        colors = theme_manager().current
        if is_selected:
            self.setBrush(QBrush(QColor(colors.control_point_selected)))
        else:
            self.setBrush(QBrush(QColor(colors.control_point_fill)))
