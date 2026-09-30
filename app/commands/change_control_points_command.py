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
    def __init__(
        self,
        controller: Any,
        edge: Any,
        old_points: list[QPointF],
        new_points: list[QPointF],
    ) -> None:
        super().__init__(tr("Move control point"))
        self._controller = controller
        self._edge = edge
        self._old_points = [QPointF(p) for p in old_points]
        self._new_points = [QPointF(p) for p in new_points]

    def redo(self) -> None:
        self._apply(self._new_points)

    def undo(self) -> None:
        self._apply(self._old_points)

    def _apply(self, points: list[QPointF]) -> None:
        self._edge.control_points = [QPointF(p) for p in points]
        self._edge._update_handles_position()
        self._edge.update_position()
