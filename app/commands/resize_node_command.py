# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------

from typing import Any

from PyQt6.QtGui import QUndoCommand

from app.i18n import tr


class ResizeNodeCommand(QUndoCommand):
    """
    Resize Node Command.

    Methods:
        __init__: Initialize the instance.
        redo: Redo.
        undo: Undo.
    """

    def __init__(
        self,
        controller: Any,
        node_item: Any,
        old_radius: float,
        new_radius: float,
    ) -> None:
        """
        Initialize the instance.

        Args:
            controller (Any): The controller.
            node_item (Any): The node item.
            old_radius (float): The old radius.
            new_radius (float): The new radius.
        """
        super().__init__(tr("Resize"))
        self._controller = controller
        self._node_item = node_item
        self._old_radius = old_radius
        self._new_radius = new_radius

    def redo(self) -> None:
        """Redo."""
        self._apply_radius(self._new_radius)

    def undo(self) -> None:
        """Undo."""
        self._apply_radius(self._old_radius)

    def _apply_radius(self, radius: float) -> None:
        """
        Apply Radius.

        Args:
            radius (float): The radius.
        """
        node = self._node_item
        if hasattr(node, "set_radius"):
            node.set_radius(radius)
        elif hasattr(node, "model") and hasattr(node.model, "radius"):
            node.model.radius = radius
            node.update()
