from typing import Any

from PyQt6.QtGui import QUndoCommand
from PyQt6.QtWidgets import QGraphicsItem

from app.ui.components.base_edge_item import BaseEdgeItem


class AddEdgeCommand(QUndoCommand):
    def __init__(
        self,
        controller: Any,
        edge: BaseEdgeItem,
        parent_item: QGraphicsItem | None = None,
    ) -> None:
        super().__init__("Añadir flecha")
        self._controller = controller
        self._edge = edge
        self._parent_item = parent_item

    def redo(self) -> None:
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
        edge_scene = self._edge.scene()
        if edge_scene is not None:
            if hasattr(self._edge, "cleanup"):
                self._edge.cleanup()
            edge_scene.removeItem(self._edge)
        if self._edge in self._controller.edges:
            self._controller.edges.remove(self._edge)
