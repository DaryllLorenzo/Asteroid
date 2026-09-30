# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------

from PyQt6.QtCore import Qt
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QPainter
from PyQt6.QtGui import QWheelEvent
from PyQt6.QtWidgets import QGraphicsScene
from PyQt6.QtWidgets import QGraphicsView

from app.ui.components.base_edge_item import BaseEdgeItem
from app.ui.components.control_point_handle import ControlPointHandle
from app.ui.components.subcanvas_item import SubCanvasItem
from app.ui.theme_manager import theme_manager


class Canvas(QGraphicsView):
    """The QGraphicsView hosting the diagram scene."""

    zoom_changed = pyqtSignal(float)
    node_dropped = pyqtSignal(str, float, float)  # type, x, y
    arrow_dropped = pyqtSignal(str)  # arrow type
    node_clicked = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self._scene = QGraphicsScene()
        self.setScene(self._scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.setBackgroundBrush(Qt.GlobalColor.white)
        self._scene.setBackgroundBrush(Qt.GlobalColor.white)

        self.setAcceptDrops(True)

        self.zoom_factor = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 5.0

        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

    def apply_theme(self, dark: bool):
        """Apply theme to canvas background."""
        colors = theme_manager().current
        bg = colors.canvas_bg
        from PyQt6.QtGui import QColor

        self.setBackgroundBrush(QColor(bg))
        self._scene.setBackgroundBrush(QColor(bg))

    # ---------------------
    # Drag & Drop
    # ---------------------
    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        if not event.mimeData().hasText():
            return

        item_type = event.mimeData().text()
        scene_pos = self.mapToScene(event.position().toPoint())

        # Check whether the drop landed on a subcanvas first.
        viewport_pos = event.position().toPoint()
        items = self.items(viewport_pos)
        for it in items:
            if hasattr(it, "subnode_dropped") or hasattr(it, "subarrow_dropped"):
                local_pt = it.mapFromScene(scene_pos)
                if item_type in [
                    "simple",
                    "dashed",
                    "dependency_link",
                    "why_link",
                    "or_decomposition",
                    "and_decomposition",
                    "contribution",
                    "means_end",
                ]:
                    it.subarrow_dropped.emit(item_type)
                else:
                    it.subnode_dropped.emit(
                        item_type, float(local_pt.x()), float(local_pt.y())
                    )
                event.acceptProposedAction()
                return

        # No subcanvas under the cursor: drop on the main canvas.
        if item_type in [
            "actor",
            "agent",
            "hard_goal",
            "soft_goal",
            "plan",
            "resource",
        ]:
            self.node_dropped.emit(item_type, scene_pos.x(), scene_pos.y())
            event.acceptProposedAction()
        elif item_type in [
            "simple",
            "dashed",
            "dependency_link",
            "why_link",
            "or_decomposition",
            "and_decomposition",
            "contribution",
            "means_end",
        ]:
            self.arrow_dropped.emit(item_type)
            event.acceptProposedAction()

    def mousePressEvent(self, event):
        items = self.items(event.pos())

        # Prefer a regular node (including ones with a subcanvas) over an
        # edge or a subcanvas item.
        for item in items:
            if not isinstance(item, (BaseEdgeItem, SubCanvasItem)):
                self.node_clicked.emit(item)
                super().mousePressEvent(event)
                return

            if isinstance(item, SubCanvasItem):
                parent = item.parentItem()
                # Walk up until we find a node that isn't itself a subcanvas.
                while parent is not None and isinstance(parent, SubCanvasItem):
                    parent = parent.parentItem()

                if parent is not None and not isinstance(parent, BaseEdgeItem):
                    self.node_clicked.emit(parent)
                super().mousePressEvent(event)
                return

        if items:
            self.node_clicked.emit(items[0])
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        scene_pos = self.mapToScene(event.position().toPoint())
        items = self.items(event.position().toPoint())

        for item in items:
            if isinstance(item, BaseEdgeItem) and not isinstance(
                item, ControlPointHandle
            ):
                item.add_control_point(scene_pos)
                item.setSelected(True)
                return

        super().mouseDoubleClickEvent(event)

    def mouseMoveEvent(self, event):
        items = self.items(event.position().toPoint())

        cursor_over_handle = False
        for item in items:
            if isinstance(item, ControlPointHandle):
                cursor_over_handle = True
                break

        if cursor_over_handle:
            self.setCursor(Qt.CursorShape.SizeAllCursor)
        else:
            cursor_over_edge = False
            for item in items:
                if isinstance(item, BaseEdgeItem) and item.isSelected():
                    cursor_over_edge = True
                    break

            if cursor_over_edge:
                self.setCursor(Qt.CursorShape.PointingHandCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)

        super().mouseMoveEvent(event)

    # ---------------------
    # Zoom
    # ---------------------
    def wheelEvent(self, event: QWheelEvent | None) -> None:
        if event is None:
            return

        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            angle = event.angleDelta().y()
            factor = 1.1 if angle > 0 else 0.9

            new_zoom = self.zoom_factor * factor
            if self.min_zoom <= new_zoom <= self.max_zoom:
                self.zoom_factor = new_zoom
                self.scale(factor, factor)
                self.zoom_changed.emit(self.zoom_factor)
        else:
            super().wheelEvent(event)

    def zoom_in(self):
        factor = 1.2
        new_zoom = self.zoom_factor * factor
        if new_zoom <= self.max_zoom:
            self.zoom_factor = new_zoom
            self.scale(factor, factor)
            self.zoom_changed.emit(self.zoom_factor)

    def zoom_out(self):
        factor = 0.8
        new_zoom = self.zoom_factor * factor
        if new_zoom >= self.min_zoom:
            self.zoom_factor = new_zoom
            self.scale(factor, factor)
            self.zoom_changed.emit(self.zoom_factor)

    def reset_zoom(self):
        self.resetTransform()
        self.zoom_factor = 1.0
        self.zoom_changed.emit(self.zoom_factor)

    def keyPressEvent(self, event):
        # Delete/Ctrl+D are already handled by QShortcut elsewhere.
        super().keyPressEvent(event)
