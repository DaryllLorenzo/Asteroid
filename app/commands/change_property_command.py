# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------

from typing import Any

from PyQt6.QtGui import QUndoCommand

from app.model_types import PropertyMap


class ChangePropertyCommand(QUndoCommand):
    """
    Change Property Command.

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
        node_item: Any,
        old_properties: PropertyMap,
        new_properties: PropertyMap,
    ) -> None:
        """
        Initialize the instance.

        Args:
            controller (Any): The controller.
            node_item (Any): The node item.
            old_properties (PropertyMap): The old properties.
            new_properties (PropertyMap): The new properties.
        """
        super().__init__("Cambiar propiedades")
        self._controller = controller
        self._node_item = node_item
        self._old_properties = old_properties
        self._new_properties = new_properties

    def id(self) -> int:
        """
        Id.

        Returns:
            int: Id.
        """
        return 1001

    def redo(self) -> None:
        """Redo."""
        if hasattr(self._node_item, "update_properties"):
            self._node_item.update_properties(self._new_properties)
        if hasattr(self._node_item, "update"):
            self._node_item.update()

    def undo(self) -> None:
        """Undo."""
        if hasattr(self._node_item, "update_properties"):
            self._node_item.update_properties(self._old_properties)
        if hasattr(self._node_item, "update"):
            self._node_item.update()

    def mergeWith(self, other: QUndoCommand) -> bool:  # type: ignore[override]
        """
        Mergewith.

        Args:
            other (QUndoCommand): The other.

        Returns:
            bool: Mergewith.
        """
        if not isinstance(other, ChangePropertyCommand):
            return False
        if other._node_item is not self._node_item:
            return False
        self._new_properties.update(other._new_properties)
        return True
