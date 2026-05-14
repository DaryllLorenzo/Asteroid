from __future__ import annotations

from collections.abc import Callable
from typing import Any
from typing import Protocol

type PropertyMap = dict[str, Any]
type ChangeCallback = Callable[[str, object], None]


class NodeModelLike(Protocol):
    """
    Node Model Like.

    Attributes:
        x (float): x.
        y (float): y.
        radius (float): radius.
        label (str): label.
        color (str): color.
        border_color (str): border color.
        text_color (str): text color.
        text_align (str): text align.
        text_width (float): text width.
        font_size (float): font size.
        content_offset_x (float): content offset x.
        content_offset_y (float): content offset y.
        position_in_subcanvas_x (float): position in subcanvas x.
        position_in_subcanvas_y (float): position in subcanvas y.
        child_nodes (list[object]): child nodes.
        show_subcanvas (bool): show subcanvas.

    Methods:
        toggle_subcanvas: Toggle Subcanvas.
        node_type: Node Type.
    """

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
    """
    Composite Model Like.

    Methods:
        add_change_callback: Add Change Callback.
        get_external_model: Get External Model.
        get_internal_model: Get Internal Model.
    """

    def add_change_callback(self, callback: ChangeCallback) -> None: ...

    def get_external_model(self) -> NodeModelLike: ...

    def get_internal_model(self) -> NodeModelLike: ...


class ModelFactory(Protocol):
    """Model Factory."""

    def __call__(
        self,
        x: float = 0,
        y: float = 0,
        radius: float = 50,
    ) -> NodeModelLike: ...
