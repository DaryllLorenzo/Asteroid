# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------

from typing import Any

from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QUndoCommand

from app.i18n import tr


class ChangeControlPointsCommand(QUndoCommand):
    """
    Change Control Points Command.

    Methods:
        __init__: Initialize the instance.
        redo: Redo.
        undo: Undo.
    """

    def __init__(
        self,
        controller: Any,
        edge: Any,
        old_points: list[QPointF],
        new_points: list[QPointF],
    ) -> None:
        """
        Initialize the instance.

        Args:
            controller (Any): The controller.
            edge (Any): The edge.
            old_points (list[QPointF]): The old points.
            new_points (list[QPointF]): The new points.
        """
        super().__init__(tr("Move control point"))
        self._controller = controller
        self._edge = edge
        self._old_points = [QPointF(p) for p in old_points]
        self._new_points = [QPointF(p) for p in new_points]

    def redo(self) -> None:
        """Redo."""
        self._apply(self._new_points)

    def undo(self) -> None:
        """Undo."""
        self._apply(self._old_points)

    def _apply(self, points: list[QPointF]) -> None:
        """
        Apply.

        Args:
            points (list[QPointF]): The points.
        """
        self._edge.control_points = [QPointF(p) for p in points]
        self._edge._update_handles_position()
        self._edge.update_position()
