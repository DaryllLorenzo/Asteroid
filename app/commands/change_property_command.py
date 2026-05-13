from typing import Any

from PyQt6.QtGui import QUndoCommand

from app.model_types import PropertyMap


class ChangePropertyCommand(QUndoCommand):
    def __init__(
        self,
        controller: Any,
        node_item: Any,
        old_properties: PropertyMap,
        new_properties: PropertyMap,
    ) -> None:
        super().__init__("Cambiar propiedades")
        self._controller = controller
        self._node_item = node_item
        self._old_properties = old_properties
        self._new_properties = new_properties

    def id(self) -> int:
        return 1001

    def redo(self) -> None:
        if hasattr(self._node_item, "update_properties"):
            self._node_item.update_properties(self._new_properties)
        if hasattr(self._node_item, "update"):
            self._node_item.update()

    def undo(self) -> None:
        if hasattr(self._node_item, "update_properties"):
            self._node_item.update_properties(self._old_properties)
        if hasattr(self._node_item, "update"):
            self._node_item.update()

    def mergeWith(self, other: QUndoCommand) -> bool:  # type: ignore[override]
        if not isinstance(other, ChangePropertyCommand):
            return False
        if other._node_item is not self._node_item:
            return False
        self._new_properties.update(other._new_properties)
        return True
