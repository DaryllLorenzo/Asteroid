# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol

from app.ui.components.base_edge_item import BaseEdgeItem
from app.ui.components.base_node_item import BaseNodeItem
from app.ui.components.base_tropos_item import BaseTroposItem
from app.ui.components.subcanvas_item import SubCanvasItem

type CanvasNodeItem = BaseNodeItem | BaseTroposItem
type CanvasSelection = CanvasNodeItem | BaseEdgeItem | None
type SubcanvasHandler = tuple[
    SubCanvasItem,
    Callable[..., object],
    Callable[..., object],
]


class NodeItemFactory(Protocol):
    """Node Item Factory."""

    def __call__(
        self,
        x: float = 0,
        y: float = 0,
        radius: float = 50,
    ) -> CanvasNodeItem: ...
