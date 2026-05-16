# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------

from typing import Any

from PyQt6.QtGui import QUndoCommand

from app.i18n import tr
from app.ui.components.base_edge_item import BaseEdgeItem


class DeleteEdgeCommand(QUndoCommand):
    """
    Delete Edge Command.

    Methods:
        __init__: Initialize the instance.
        redo: Redo.
        undo: Undo.
    """

    def __init__(self, controller: Any, edge: BaseEdgeItem) -> None:
        """
        Initialize the instance.

        Args:
            controller (Any): The controller.
            edge (BaseEdgeItem): The edge.
        """
        super().__init__(tr("Delete arrow"))
        self._controller = controller
        self._edge = edge
        self._node_source = edge.source_node
        self._node_dest = edge.dest_node
        self._parent_item = edge.parentItem()

    def redo(self) -> None:
        """Redo."""
        edge_scene = self._edge.scene()
        if edge_scene is not None:
            if hasattr(self._edge, "cleanup"):
                self._edge.cleanup()
            edge_scene.removeItem(self._edge)
        if self._edge in self._controller.edges:
            self._controller.edges.remove(self._edge)

        if self._edge == self._controller.selected_edge:
            self._controller.selected_edge = None
            self._controller.current_selection = None
            self._controller.edge_selected.emit(None)
            self._controller.selection_changed.emit(None)

    def undo(self) -> None:
        """Undo."""
        parent = self._parent_item
        if self._edge.scene() is None:
            if parent is not None and parent.scene() is not None:
                self._edge.setParentItem(parent)
            else:
                scene = self._controller.canvas.scene()
                if scene is not None:
                    scene.addItem(self._edge)
        if self._edge not in self._controller.edges:
            self._controller.edges.append(self._edge)
        if hasattr(self._edge, "_connect_to_nodes"):
            self._edge._connect_to_nodes()
        self._edge.update_position()
