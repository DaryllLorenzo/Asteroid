# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------

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
from app.validation.validator import Validator


class SignalLike(Protocol):
    """
    Signal Like.

    Methods:
        emit: Emit.
    """

    def emit(self, *args: object) -> object: ...


class CanvasControllerMixin:
    """
    Canvas Controller Mixin.

    Attributes:
        canvas (Canvas): canvas.
        nodes (list[CanvasNodeItem]): nodes.
        edges (list[BaseEdgeItem]): edges.
        arrow_mode (bool): arrow mode.
        selected_arrow_type (str | None): selected arrow type.
        selected_nodes_for_arrow (list[CanvasNodeItem]): selected nodes for arrow.
        composite_mode (bool): composite mode.
        composite_node_type (str | None): composite node type.
        selection_mode (bool): selection mode.
        selected_node (CanvasNodeItem | None): selected node.
        selected_edge (BaseEdgeItem | None): selected edge.
        current_selection (CanvasSelection): current selection.
        _current_subcanvas (SubCanvasItem | None): current subcanvas.
        _subcanvas_handlers (dict[CanvasNodeItem, SubcanvasHandler]): subcanvas
        handlers.
        _current_file_path (str | None): current file path.
        _is_modified (bool): is modified.
        delete_shortcut (QShortcut): delete shortcut.
        delete_shortcut2 (QShortcut): delete shortcut2.
        undo_stack (QUndoStack): undo stack.
        validator (Validator): validator.
        node_selected (SignalLike): node selected.
        selected_node_properties_changed (SignalLike): selected node properties changed.
        node_deleted (SignalLike): node deleted.
        edge_selected (SignalLike): edge selected.
        edge_deleted (SignalLike): edge deleted.
        selection_changed (SignalLike): selection changed.
        project_modified (SignalLike): project modified.

    Methods:
        add_node: Add Node.
        clear_canvas: Clear Canvas.
        create_arrow: Create Arrow.
        create_composite_dependency: Create Composite Dependency.
        delete_edge: Delete Edge.
        delete_node: Delete Node.
        delete_selected_edge: Delete Selected Edge.
        delete_selected_item: Delete Selected Item.
        delete_selected_node: Delete Selected Node.
        handle_node_click: Handle Node Click.
        mark_as_modified: Mark As Modified.
        mark_as_saved: Mark As Saved.
        on_node_properties_changed: On Node Properties Changed.
        on_selection_changed: On Selection Changed.
        start_arrow_mode: Start Arrow Mode.
        start_composite_dependency_mode: Start Composite Dependency Mode.
        update_node_properties: Update Node Properties.
    """

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
    validator: Validator
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
        """
        Add Node.

        Args:
            node_type (str): The node type.
            x (float): The x.
            y (float): The y.

        Returns:
            CanvasNodeItem | None: Add Node.

        Raises:
            NotImplementedError: If an error occurs.
        """
        raise NotImplementedError

    def clear_canvas(self) -> None:
        """
        Clear Canvas.

        Raises:
            NotImplementedError: If an error occurs.
        """
        raise NotImplementedError

    def create_arrow(self):
        """
        Create Arrow.

        Raises:
            NotImplementedError: If an error occurs.
        """
        raise NotImplementedError

    def create_composite_dependency(self):
        """
        Create Composite Dependency.

        Raises:
            NotImplementedError: If an error occurs.
        """
        raise NotImplementedError

    def delete_edge(self, edge_to_delete: BaseEdgeItem) -> None:
        """
        Delete Edge.

        Args:
            edge_to_delete (BaseEdgeItem): The edge to delete.

        Raises:
            NotImplementedError: If an error occurs.
        """
        raise NotImplementedError

    def delete_node(self, node_to_delete: CanvasNodeItem) -> None:
        """
        Delete Node.

        Args:
            node_to_delete (CanvasNodeItem): The node to delete.

        Raises:
            NotImplementedError: If an error occurs.
        """
        raise NotImplementedError

    def delete_selected_edge(self) -> None:
        """
        Delete Selected Edge.

        Raises:
            NotImplementedError: If an error occurs.
        """
        raise NotImplementedError

    def delete_selected_item(self) -> None:
        """
        Delete Selected Item.

        Raises:
            NotImplementedError: If an error occurs.
        """
        raise NotImplementedError

    def delete_selected_node(self) -> None:
        """
        Delete Selected Node.

        Raises:
            NotImplementedError: If an error occurs.
        """
        raise NotImplementedError

    def handle_node_click(self, node_item: object) -> None:
        """
        Handle Node Click.

        Args:
            node_item (object): The node item.

        Raises:
            NotImplementedError: If an error occurs.
        """
        raise NotImplementedError

    def mark_as_modified(self) -> None:
        """
        Mark As Modified.

        Raises:
            NotImplementedError: If an error occurs.
        """
        raise NotImplementedError

    def mark_as_saved(self, file_path: str | None = None) -> None:
        """
        Mark As Saved.

        Args:
            file_path (str | None): The file path.

        Raises:
            NotImplementedError: If an error occurs.
        """
        raise NotImplementedError

    def on_node_properties_changed(
        self,
        node_item: CanvasNodeItem,
        properties: PropertyMap,
    ) -> None:
        """
        On Node Properties Changed.

        Args:
            node_item (CanvasNodeItem): The node item.
            properties (PropertyMap): The properties.

        Raises:
            NotImplementedError: If an error occurs.
        """
        raise NotImplementedError

    def on_selection_changed(self) -> None:
        """
        On Selection Changed.

        Raises:
            NotImplementedError: If an error occurs.
        """
        raise NotImplementedError

    def start_arrow_mode(self, arrow_type: str) -> None:
        """
        Start Arrow Mode.

        Args:
            arrow_type (str): The arrow type.

        Raises:
            NotImplementedError: If an error occurs.
        """
        raise NotImplementedError

    def start_composite_dependency_mode(self, node_type: str) -> None:
        """
        Start Composite Dependency Mode.

        Args:
            node_type (str): The node type.

        Raises:
            NotImplementedError: If an error occurs.
        """
        raise NotImplementedError

    def _start_subarrow_mode(
        self,
        parent_node_item: CanvasNodeItem,
        subcanvas: SubCanvasItem,
        arrow_type: str,
    ) -> None:
        """
        Start Subarrow Mode.

        Args:
            parent_node_item (CanvasNodeItem): The parent node item.
            subcanvas (SubCanvasItem): The subcanvas.
            arrow_type (str): The arrow type.

        Raises:
            NotImplementedError: If an error occurs.
        """
        raise NotImplementedError

    def update_node_properties(self, properties: PropertyMap) -> None:
        """
        Update Node Properties.

        Args:
            properties (PropertyMap): The properties.

        Raises:
            NotImplementedError: If an error occurs.
        """
        raise NotImplementedError

    def _remove_node_clean(self, node: CanvasNodeItem) -> None:
        """
        Remove Node Clean.

        Args:
            node (CanvasNodeItem): The node.

        Raises:
            NotImplementedError: If an error occurs.
        """
        raise NotImplementedError

    def _restore_node(self, node_item: CanvasNodeItem) -> None:
        """
        Restore Node.

        Args:
            node_item (CanvasNodeItem): The node item.

        Raises:
            NotImplementedError: If an error occurs.
        """
        raise NotImplementedError

    def _on_node_drag_finished(
        self,
        node_item: CanvasNodeItem,
        start_pos: object,
    ) -> None:
        """
        On Node Drag Finished.

        Args:
            node_item (CanvasNodeItem): The node item.
            start_pos (object): The start pos.

        Raises:
            NotImplementedError: If an error occurs.
        """
        raise NotImplementedError

    def _on_node_resize_finished(
        self,
        node_item: object,
        old_radius: float,
    ) -> None:
        """
        On Node Resize Finished.

        Args:
            node_item (object): The node item.
            old_radius (float): The old radius.

        Raises:
            NotImplementedError: If an error occurs.
        """
        raise NotImplementedError

    def _on_subcanvas_toggle_requested(
        self,
        node_item: object,
    ) -> None:
        """
        On Subcanvas Toggle Requested.

        Args:
            node_item (object): The node item.

        Raises:
            NotImplementedError: If an error occurs.
        """
        raise NotImplementedError

    def _on_subcanvas_node_dropped(
        self,
        parent_node_item: CanvasNodeItem,
        subcanvas: object,
        item_type: str,
        local_x: float,
        local_y: float,
    ) -> None:
        """
        On Subcanvas Node Dropped.

        Args:
            parent_node_item (CanvasNodeItem): The parent node item.
            subcanvas (object): The subcanvas.
            item_type (str): The item type.
            local_x (float): The local x.
            local_y (float): The local y.

        Raises:
            NotImplementedError: If an error occurs.
        """
        raise NotImplementedError

    def _show_validation_errors(self, errors: list[str]) -> None:
        """
        Show Validation Errors.

        Args:
            errors (list[str]): The errors.

        Raises:
            NotImplementedError: If an error occurs.
        """
        raise NotImplementedError

    def _connect_edge_undo_tracking(self, edge: object) -> None:
        """
        Connect Edge Undo Tracking.

        Args:
            edge (object): The edge.

        Raises:
            NotImplementedError: If an error occurs.
        """
        raise NotImplementedError

    def _collect_edges_for_node(
        self,
        node_item: CanvasNodeItem,
    ) -> list[dict]:
        """
        Collect Edges For Node.

        Args:
            node_item (CanvasNodeItem): The node item.

        Returns:
            list[dict]: Collect Edges For Node.

        Raises:
            NotImplementedError: If an error occurs.
        """
        raise NotImplementedError
