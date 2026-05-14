# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------

from typing import Any

from PyQt6.QtGui import QUndoCommand
from PyQt6.QtWidgets import QGraphicsItem

from app.ui.components.base_edge_item import BaseEdgeItem


class AddEdgeCommand(QUndoCommand):
    """
    Add Edge Command.

    Methods:
        __init__: Initialize the instance.
        redo: Redo.
        undo: Undo.
    """

    def __init__(
        self,
        controller: Any,
        edge: BaseEdgeItem,
        parent_item: QGraphicsItem | None = None,
    ) -> None:
        """
        Initialize the instance.

        Args:
            controller (Any): The controller.
            edge (BaseEdgeItem): The edge.
            parent_item (QGraphicsItem | None): The parent item.
        """
        super().__init__("Añadir flecha")
        self._controller = controller
        self._edge = edge
        self._parent_item = parent_item

    def redo(self) -> None:
        """Redo."""
        if self._edge.scene() is None:
            parent = self._parent_item
            if parent is not None and parent.scene() is not None:
                self._edge.setParentItem(parent)
                self._edge.update_position()
            else:
                scene = self._controller.canvas.scene()
                if scene is not None:
                    scene.addItem(self._edge)
        if self._edge not in self._controller.edges:
            self._controller.edges.append(self._edge)
        if hasattr(self._edge, "_connect_to_nodes"):
            self._edge._connect_to_nodes()
        if hasattr(self._controller, "_connect_edge_undo_tracking"):
            self._controller._connect_edge_undo_tracking(self._edge)
        self._edge.update_position()

    def undo(self) -> None:
        """Undo."""
        edge_scene = self._edge.scene()
        if edge_scene is not None:
            if hasattr(self._edge, "cleanup"):
                self._edge.cleanup()
            edge_scene.removeItem(self._edge)
        if self._edge in self._controller.edges:
            self._controller.edges.remove(self._edge)
