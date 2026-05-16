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
    """
    Canvas.

    Methods:
        __init__: Initialize the instance.
        dragEnterEvent: Dragenterevent.
        dragMoveEvent: Dragmoveevent.
        dropEvent: Dropevent.
        mousePressEvent: Mousepressevent.
        mouseDoubleClickEvent: Mousedoubleclickevent.
        mouseMoveEvent: Mousemoveevent.
        wheelEvent: Wheelevent.
        zoom_in: Zoom In.
        zoom_out: Zoom Out.
        reset_zoom: Reset Zoom.
        keyPressEvent: Keypressevent.
    """

    zoom_changed = pyqtSignal(float)  # New factor of zoom
    node_dropped = pyqtSignal(str, float, float)  # type, x, y
    arrow_dropped = pyqtSignal(str)  # type of flecha
    node_clicked = pyqtSignal(object)  # for controladores

    def __init__(self):
        """Initialize the instance."""
        super().__init__()
        self._scene = QGraphicsScene()
        self.setScene(self._scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)

        # White background
        self.setBackgroundBrush(Qt.GlobalColor.white)
        self._scene.setBackgroundBrush(Qt.GlobalColor.white)

        # Drag & Drop
        self.setAcceptDrops(True)

        # Zoom
        self.zoom_factor = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 5.0

        # Configuration of vista
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
        """
        Dragenterevent.

        Args:
            event: The event.
        """
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        """
        Dragmoveevent.

        Args:
            event: The event.
        """
        event.acceptProposedAction()

    def dropEvent(self, event):
        """
        Dropevent.

        Args:
            event: The event.
        """
        if not event.mimeData().hasText():
            return

        item_type = event.mimeData().text()
        scene_pos = self.mapToScene(event.position().toPoint())

        # review if itself dropped over a subcanvas
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
                    # forward a subcanvas
                    it.subarrow_dropped.emit(item_type)
                else:
                    # forward a subcanvas node
                    it.subnode_dropped.emit(
                        item_type, float(local_pt.x()), float(local_pt.y())
                    )
                event.acceptProposedAction()
                return

        # if no there is subcanvas below, dropeo global
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
        """
        Mousepressevent.

        Args:
            event: The event.
        """
        items = self.items(event.pos())

        # Prioridad: first buscar nodes regulares
        # (incluyendo nodes parent with subcanvas)
        for item in items:
            # If es a node regular (no edge, no subcanvas)
            if not isinstance(item, (BaseEdgeItem, SubCanvasItem)):
                self.node_clicked.emit(item)
                super().mousePressEvent(event)
                return

            # If it's a subcanvas, find the parent node and emit that
            if isinstance(item, SubCanvasItem):
                parent = item.parentItem()
                # Buscar recursivamente until find a node that no sea subcanvas
                while parent is not None and isinstance(parent, SubCanvasItem):
                    parent = parent.parentItem()

                # If we find a node parent valid, usarlo
                if parent is not None and not isinstance(parent, BaseEdgeItem):
                    self.node_clicked.emit(parent)
                else:
                    # If no there is parent valid, ignore
                    pass
                super().mousePressEvent(event)
                return

        # Comportamiento por defecto
        if items:
            self.node_clicked.emit(items[0])
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        """
        Mousedoubleclickevent.

        Args:
            event: The event.
        """
        scene_pos = self.mapToScene(event.position().toPoint())
        items = self.items(event.position().toPoint())

        # Buscar if there is a edge under the cursor
        for item in items:
            if isinstance(item, BaseEdgeItem) and not isinstance(
                item, ControlPointHandle
            ):
                # Add control point in the position of the doble-click
                item.add_control_point(scene_pos)
                # Seleccionar the edge for show the handles
                item.setSelected(True)
                return

        # If no es in a edge, comportamiento by defecto
        super().mouseDoubleClickEvent(event)

    def mouseMoveEvent(self, event):
        """
        Mousemoveevent.

        Args:
            event: The event.
        """
        items = self.items(event.position().toPoint())

        # Buscar if there is a handle under the cursor
        cursor_over_handle = False
        for item in items:
            if isinstance(item, ControlPointHandle):
                cursor_over_handle = True
                break

        if cursor_over_handle:
            self.setCursor(Qt.CursorShape.SizeAllCursor)
        else:
            # Verificar if this over a edge
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
        """
        Wheelevent.

        Args:
            event (QWheelEvent | None): The event.
        """
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
        """Zoom In."""
        factor = 1.2
        new_zoom = self.zoom_factor * factor
        if new_zoom <= self.max_zoom:
            self.zoom_factor = new_zoom
            self.scale(factor, factor)
            self.zoom_changed.emit(self.zoom_factor)

    def zoom_out(self):
        """Zoom Out."""
        factor = 0.8
        new_zoom = self.zoom_factor * factor
        if new_zoom >= self.min_zoom:
            self.zoom_factor = new_zoom
            self.scale(factor, factor)
            self.zoom_changed.emit(self.zoom_factor)

    def reset_zoom(self):
        """Reset Zoom."""
        self.resetTransform()
        self.zoom_factor = 1.0
        self.zoom_changed.emit(self.zoom_factor)

    def keyPressEvent(self, event):
        """
        Keypressevent.

        Args:
            event: The event.
        """
        # Delegar the manejo of keys al controlador
        # The keys Delete y Ctrl+D already están handled by the QShortcut
        super().keyPressEvent(event)
