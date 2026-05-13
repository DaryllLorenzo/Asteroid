from typing import Any

from PyQt6.QtGui import QUndoCommand


class ToggleSubcanvasCommand(QUndoCommand):
    def __init__(self, controller: Any, node_item: Any) -> None:
        was_open = getattr(node_item.model, "show_subcanvas", False)
        super().__init__("Cerrar subcanvas" if was_open else "Abrir subcanvas")
        self._controller = controller
        self._node_item = node_item

    def redo(self) -> None:
        if hasattr(self._node_item, "_toggle_subcanvas"):
            self._node_item._toggle_subcanvas()

    def undo(self) -> None:
        if hasattr(self._node_item, "_toggle_subcanvas"):
            self._node_item._toggle_subcanvas()
