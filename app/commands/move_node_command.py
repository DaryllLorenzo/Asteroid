from typing import Any

from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QUndoCommand

from app.controller_types import CanvasNodeItem


class MoveNodeCommand(QUndoCommand):
    def __init__(
        self,
        controller: Any,
        node_item: CanvasNodeItem,
        old_pos: QPointF,
        new_pos: QPointF,
    ) -> None:
        super().__init__("Mover nodo")
        self._controller = controller
        self._node_item = node_item
        self._old_pos = old_pos
        self._new_pos = new_pos

    def id(self) -> int:
        return 1002

    def redo(self) -> None:
        self._node_item.setPos(self._new_pos)
        if hasattr(self._node_item, "model") and hasattr(self._node_item.model, "x"):
            self._node_item.model.x = self._new_pos.x()
        if hasattr(self._node_item, "model") and hasattr(self._node_item.model, "y"):
            self._node_item.model.y = self._new_pos.y()

    def undo(self) -> None:
        self._node_item.setPos(self._old_pos)
        if hasattr(self._node_item, "model") and hasattr(self._node_item.model, "x"):
            self._node_item.model.x = self._old_pos.x()
        if hasattr(self._node_item, "model") and hasattr(self._node_item.model, "y"):
            self._node_item.model.y = self._old_pos.y()

    def mergeWith(self, other: QUndoCommand) -> bool:  # type: ignore[override]
        if not isinstance(other, MoveNodeCommand):
            return False
        if other._node_item is not self._node_item:
            return False
        self._new_pos = other._new_pos
        return True
