from __future__ import annotations

from typing import Protocol

from PyQt6.QtGui import QShortcut
from PyQt6.QtGui import QUndoStack

from app.controller_types import CanvasNodeItem
from app.controller_types import CanvasSelection
from app.controller_types import SubcanvasHandler
from app.model_types import PropertyMap
from app.ui.canvas import Canvas
from app.ui.components.base_edge_item import BaseEdgeItem
from app.ui.components.subcanvas_item import SubCanvasItem


class SignalLike(Protocol):
    def emit(self, *args: object) -> object: ...


class CanvasControllerMixin:
    canvas: Canvas
    nodes: list[CanvasNodeItem]
    edges: list[BaseEdgeItem]
    arrow_mode: bool
    selected_arrow_type: str | None
    selected_nodes_for_arrow: list[CanvasNodeItem]
    composite_mode: bool
    composite_node_type: str | None
    selection_mode: bool
    selected_node: CanvasNodeItem | None
    selected_edge: BaseEdgeItem | None
    current_selection: CanvasSelection
    _current_subcanvas: SubCanvasItem | None
    _subcanvas_handlers: dict[CanvasNodeItem, SubcanvasHandler]
    _current_file_path: str | None
    _is_modified: bool
    delete_shortcut: QShortcut
    delete_shortcut2: QShortcut
    undo_stack: QUndoStack
    node_selected: SignalLike
    selected_node_properties_changed: SignalLike
    node_deleted: SignalLike
    edge_selected: SignalLike
    edge_deleted: SignalLike
    selection_changed: SignalLike
    project_modified: SignalLike

    def add_node(
        self,
        node_type: str,
        x: float,
        y: float,
    ) -> CanvasNodeItem | None:
        raise NotImplementedError

    def clear_canvas(self) -> None:
        raise NotImplementedError

    def create_arrow(self):
        raise NotImplementedError

    def create_composite_dependency(self):
        raise NotImplementedError

    def delete_edge(self, edge_to_delete: BaseEdgeItem) -> None:
        raise NotImplementedError

    def delete_node(self, node_to_delete: CanvasNodeItem) -> None:
        raise NotImplementedError

    def delete_selected_edge(self) -> None:
        raise NotImplementedError

    def delete_selected_item(self) -> None:
        raise NotImplementedError

    def delete_selected_node(self) -> None:
        raise NotImplementedError

    def handle_node_click(self, node_item: object) -> None:
        raise NotImplementedError

    def mark_as_modified(self) -> None:
        raise NotImplementedError

    def mark_as_saved(self, file_path: str | None = None) -> None:
        raise NotImplementedError

    def on_node_properties_changed(
        self,
        node_item: CanvasNodeItem,
        properties: PropertyMap,
    ) -> None:
        raise NotImplementedError

    def on_selection_changed(self) -> None:
        raise NotImplementedError

    def start_arrow_mode(self, arrow_type: str) -> None:
        raise NotImplementedError

    def start_composite_dependency_mode(self, node_type: str) -> None:
        raise NotImplementedError

    def _start_subarrow_mode(
        self,
        parent_node_item: CanvasNodeItem,
        subcanvas: SubCanvasItem,
        arrow_type: str,
    ) -> None:
        raise NotImplementedError

    def update_node_properties(self, properties: PropertyMap) -> None:
        raise NotImplementedError

    def _remove_node_clean(self, node: CanvasNodeItem) -> None:
        raise NotImplementedError

    def _restore_node(self, node_item: CanvasNodeItem) -> None:
        raise NotImplementedError

    def _on_node_drag_finished(
        self,
        node_item: CanvasNodeItem,
        start_pos: object,
    ) -> None:
        raise NotImplementedError

    def _on_node_resize_finished(
        self,
        node_item: object,
        old_radius: float,
    ) -> None:
        raise NotImplementedError

    def _on_subcanvas_toggle_requested(
        self,
        node_item: object,
    ) -> None:
        raise NotImplementedError

    def _on_subcanvas_node_dropped(
        self,
        parent_node_item: CanvasNodeItem,
        subcanvas: object,
        item_type: str,
        local_x: float,
        local_y: float,
    ) -> None:
        raise NotImplementedError

    def _collect_edges_for_node(
        self,
        node_item: CanvasNodeItem,
    ) -> list[dict]:
        raise NotImplementedError
