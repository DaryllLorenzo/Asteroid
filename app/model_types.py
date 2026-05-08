from __future__ import annotations

from collections.abc import Callable
from typing import Any
from typing import Protocol

type PropertyMap = dict[str, Any]
type ChangeCallback = Callable[[str, object], None]


class NodeModelLike(Protocol):
    x: float
    y: float
    radius: float
    label: str
    color: str
    border_color: str
    text_color: str
    text_align: str
    text_width: float
    font_size: float
    content_offset_x: float
    content_offset_y: float
    position_in_subcanvas_x: float
    position_in_subcanvas_y: float
    child_nodes: list[object]
    show_subcanvas: bool

    def toggle_subcanvas(self) -> bool: ...

    def node_type(self) -> str: ...


class CompositeModelLike(NodeModelLike, Protocol):
    def add_change_callback(self, callback: ChangeCallback) -> None: ...

    def get_external_model(self) -> NodeModelLike: ...

    def get_internal_model(self) -> NodeModelLike: ...


class ModelFactory(Protocol):
    def __call__(
        self,
        x: float = 0,
        y: float = 0,
        radius: float = 50,
    ) -> NodeModelLike: ...
