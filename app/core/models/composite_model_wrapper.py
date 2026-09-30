# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------

import logging

from app.model_types import ChangeCallback
from app.model_types import NodeModelLike

logger = logging.getLogger(__name__)


class CompositeModelWrapper:
    """Pairs an external (canvas) model with an internal (subcanvas) model.

    SYNCED_PROPERTIES are written to both models and trigger change
    callbacks; everything else reads/writes only the external model.
    """

    SYNCED_PROPERTIES = {"label", "color", "border_color", "text_color"}
    _external_model: NodeModelLike
    _internal_model: NodeModelLike
    _on_change_callbacks: list[ChangeCallback]

    def __init__(
        self,
        external_model: NodeModelLike,
        internal_model: NodeModelLike,
    ) -> None:
        object.__setattr__(self, "_external_model", external_model)
        object.__setattr__(self, "_internal_model", internal_model)
        object.__setattr__(self, "_on_change_callbacks", [])

    def _notify_change(self, prop_name: str, value: object) -> None:
        callbacks: list[ChangeCallback] = self._on_change_callbacks
        for callback in callbacks:
            try:
                callback(prop_name, value)
            except Exception:
                logger.exception("Change callback failed for property %r", prop_name)

    def add_change_callback(self, callback: ChangeCallback) -> None:
        self._on_change_callbacks.append(callback)

    # ==================== SYNCED PROPERTIES ====================

    @property
    def label(self) -> str:
        return self._external_model.label

    @label.setter
    def label(self, value: str) -> None:
        self._external_model.label = value
        self._internal_model.label = value
        self._notify_change("label", value)

    @property
    def color(self) -> str:
        return self._external_model.color

    @color.setter
    def color(self, value: str) -> None:
        self._external_model.color = value
        self._internal_model.color = value
        self._notify_change("color", value)

    @property
    def border_color(self) -> str:
        return self._external_model.border_color

    @border_color.setter
    def border_color(self, value: str) -> None:
        self._external_model.border_color = value
        self._internal_model.border_color = value
        self._notify_change("border_color", value)

    @property
    def text_color(self) -> str:
        return self._external_model.text_color

    @text_color.setter
    def text_color(self, value: str) -> None:
        self._external_model.text_color = value
        self._internal_model.text_color = value
        self._notify_change("text_color", value)

    # ==================== EXTERNAL-ONLY PROPERTIES ====================

    @property
    def x(self) -> float:
        return self._external_model.x

    @x.setter
    def x(self, value: float) -> None:
        self._external_model.x = value

    @property
    def y(self) -> float:
        return self._external_model.y

    @y.setter
    def y(self, value: float) -> None:
        self._external_model.y = value

    @property
    def radius(self) -> float:
        return self._external_model.radius

    @radius.setter
    def radius(self, value: float) -> None:
        self._external_model.radius = value

    @property
    def text_align(self) -> str:
        return self._external_model.text_align

    @text_align.setter
    def text_align(self, value: str) -> None:
        self._external_model.text_align = value

    @property
    def text_width(self) -> float:
        return self._external_model.text_width

    @text_width.setter
    def text_width(self, value: float) -> None:
        self._external_model.text_width = value

    @property
    def font_size(self) -> float:
        return self._external_model.font_size

    @font_size.setter
    def font_size(self, value: float) -> None:
        self._external_model.font_size = value

    @property
    def content_offset_x(self) -> float:
        return self._external_model.content_offset_x

    @content_offset_x.setter
    def content_offset_x(self, value: float) -> None:
        self._external_model.content_offset_x = value

    @property
    def content_offset_y(self) -> float:
        return self._external_model.content_offset_y

    @content_offset_y.setter
    def content_offset_y(self, value: float) -> None:
        self._external_model.content_offset_y = value

    @property
    def position_in_subcanvas_x(self) -> float:
        return self._external_model.position_in_subcanvas_x

    @position_in_subcanvas_x.setter
    def position_in_subcanvas_x(self, value: float) -> None:
        self._external_model.position_in_subcanvas_x = value

    @property
    def position_in_subcanvas_y(self) -> float:
        return self._external_model.position_in_subcanvas_y

    @position_in_subcanvas_y.setter
    def position_in_subcanvas_y(self, value: float) -> None:
        self._external_model.position_in_subcanvas_y = value

    @property
    def show_subcanvas(self) -> bool:
        return self._external_model.show_subcanvas

    @show_subcanvas.setter
    def show_subcanvas(self, value: bool) -> None:
        self._external_model.show_subcanvas = value

    @property
    def child_nodes(self) -> list[object]:
        return self._external_model.child_nodes

    @child_nodes.setter
    def child_nodes(self, value: list[object]) -> None:
        self._external_model.child_nodes = value

    # ==================== METHODS ====================

    def toggle_subcanvas(self) -> bool:
        return self._external_model.toggle_subcanvas()

    def node_type(self) -> str:
        return self._external_model.node_type()

    # ==================== INTERNAL MODEL ACCESS ====================

    def get_external_model(self) -> NodeModelLike:
        return self._external_model

    def get_internal_model(self) -> NodeModelLike:
        return self._internal_model

    # ==================== GENERIC DELEGATION ====================

    def __getattr__(self, name: str) -> object:
        if name.startswith("_"):
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'"
            )
        return getattr(self._external_model, name)

    def __setattr__(self, name: str, value: object) -> None:
        if name in self.SYNCED_PROPERTIES:
            setattr(self._external_model, name, value)
            setattr(self._internal_model, name, value)
            self._notify_change(name, value)
        else:
            setattr(self._external_model, name, value)
