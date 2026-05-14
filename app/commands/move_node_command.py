# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------

from typing import Any

from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QUndoCommand

from app.controller_types import CanvasNodeItem


class MoveNodeCommand(QUndoCommand):
    """
    Move Node Command.

    Methods:
        __init__: Initialize the instance.
        id: Id.
        redo: Redo.
        undo: Undo.
        mergeWith: Mergewith.
    """

    def __init__(
        self,
        controller: Any,
        node_item: CanvasNodeItem,
        old_pos: QPointF,
        new_pos: QPointF,
    ) -> None:
        """
        Initialize the instance.

        Args:
            controller (Any): The controller.
            node_item (CanvasNodeItem): The node item.
            old_pos (QPointF): The old pos.
            new_pos (QPointF): The new pos.
        """
        super().__init__("Mover nodo")
        self._controller = controller
        self._node_item = node_item
        self._old_pos = old_pos
        self._new_pos = new_pos

    def id(self) -> int:
        """
        Id.

        Returns:
            int: Id.
        """
        return 1002

    def redo(self) -> None:
        """Redo."""
        self._node_item.setPos(self._new_pos)
        if hasattr(self._node_item, "model") and hasattr(self._node_item.model, "x"):
            self._node_item.model.x = self._new_pos.x()
        if hasattr(self._node_item, "model") and hasattr(self._node_item.model, "y"):
            self._node_item.model.y = self._new_pos.y()

    def undo(self) -> None:
        """Undo."""
        self._node_item.setPos(self._old_pos)
        if hasattr(self._node_item, "model") and hasattr(self._node_item.model, "x"):
            self._node_item.model.x = self._old_pos.x()
        if hasattr(self._node_item, "model") and hasattr(self._node_item.model, "y"):
            self._node_item.model.y = self._old_pos.y()

    def mergeWith(self, other: QUndoCommand) -> bool:  # type: ignore[override]
        """
        Mergewith.

        Args:
            other (QUndoCommand): The other.

        Returns:
            bool: Mergewith.
        """
        if not isinstance(other, MoveNodeCommand):
            return False
        if other._node_item is not self._node_item:
            return False
        self._new_pos = other._new_pos
        return True
