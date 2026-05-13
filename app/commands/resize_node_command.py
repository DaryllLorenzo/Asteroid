from typing import Any

from PyQt6.QtGui import QUndoCommand


class ResizeNodeCommand(QUndoCommand):
    def __init__(
        self,
        controller: Any,
        node_item: Any,
        old_radius: float,
        new_radius: float,
    ) -> None:
        super().__init__("Cambiar tamaño")
        self._controller = controller
        self._node_item = node_item
        self._old_radius = old_radius
        self._new_radius = new_radius

    def redo(self) -> None:
        self._apply_radius(self._new_radius)

    def undo(self) -> None:
        self._apply_radius(self._old_radius)

    def _apply_radius(self, radius: float) -> None:
        node = self._node_item
        if hasattr(node, "set_radius"):
            node.set_radius(radius)
        elif hasattr(node, "model") and hasattr(node.model, "radius"):
            node.model.radius = radius
            node.update()
