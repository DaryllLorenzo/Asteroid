# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------
from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QKeySequence
from PyQt6.QtGui import QShortcut
from PyQt6.QtGui import QUndoStack

from app.commands.change_property_command import ChangePropertyCommand
from app.commands.move_node_command import MoveNodeCommand
from app.controller_types import CanvasNodeItem
from app.controllers._canvas_mixin import CanvasControllerMixin
from app.model_types import PropertyMap
from app.ui.components.base_edge_item import BaseEdgeItem
from app.ui.components.base_node_item import BaseNodeItem
from app.ui.components.base_tropos_item import BaseTroposItem


class CanvasStateController(CanvasControllerMixin):
    selection_mode: bool
    selected_node: CanvasNodeItem | None
    selected_edge: BaseEdgeItem | None
    current_selection: CanvasNodeItem | BaseEdgeItem | None
    _current_file_path: str | None
    _is_modified: bool
    delete_shortcut: QShortcut
    delete_shortcut2: QShortcut
    undo_stack: QUndoStack  # Set by CanvasController

    @property
    def is_modified(self) -> bool:
        return self._is_modified

    @is_modified.setter
    def is_modified(self, value: bool) -> None:
        if self._is_modified != value:
            self._is_modified = value
            self.project_modified.emit(value)

    def mark_as_modified(self) -> None:
        """Mark project as modified"""
        self.is_modified = True

    def mark_as_saved(
        self,
        file_path: str | None = None,
    ) -> None:
        """Mark project as saved"""
        if hasattr(self, "undo_stack"):
            self.undo_stack.setClean()
        self.is_modified = False
        if file_path:
            self._current_file_path = file_path

    def _setup_delete_shortcut(self) -> None:
        """Setup keyboard shortcut to delete selected elements"""
        self.delete_shortcut = QShortcut(QKeySequence("Delete"), self.canvas)
        self.delete_shortcut.activated.connect(self.delete_selected_item)

        self.delete_shortcut2 = QShortcut(QKeySequence("Ctrl+D"), self.canvas)
        self.delete_shortcut2.activated.connect(self.delete_selected_item)

    def _get_node_property(
        self,
        node_item: CanvasNodeItem,
        key: str,
    ) -> object:
        """Read a property value from a node item,
        matching update_properties lookup order."""
        if hasattr(node_item, "_independent_model") and node_item._independent_model:
            if hasattr(node_item._independent_model, key):
                return getattr(node_item._independent_model, key)
        if hasattr(node_item, "model") and hasattr(node_item.model, key):
            return getattr(node_item.model, key)
        if key == "x":
            return node_item.pos().x()
        if key == "y":
            return node_item.pos().y()
        return None

    def _on_node_drag_finished(
        self,
        node_item: CanvasNodeItem,
        start_pos: object,
    ) -> None:
        """Handle drag finish: push a MoveNodeCommand."""
        if not isinstance(start_pos, QPointF):
            return
        end_pos = node_item.pos()
        if start_pos != end_pos:
            self.undo_stack.push(MoveNodeCommand(self, node_item, start_pos, end_pos))

    def _on_node_resize_finished(
        self,
        node_item: object,
        old_radius: float,
    ) -> None:
        """Handle resize finish: push a ResizeNodeCommand."""
        current_radius = float(getattr(node_item, "radius", 0))
        if hasattr(node_item, "model") and hasattr(node_item.model, "radius"):
            current_radius = float(node_item.model.radius)
        if abs(old_radius - current_radius) > 0.5:
            from app.commands.resize_node_command import ResizeNodeCommand

            self.undo_stack.push(
                ResizeNodeCommand(self, node_item, old_radius, current_radius)
            )

    def _on_subcanvas_toggle_requested(
        self,
        node_item: object,
    ) -> None:
        """Handle subcanvas toggle: push a ToggleSubcanvasCommand."""
        from app.commands.toggle_subcanvas_command import ToggleSubcanvasCommand

        self.undo_stack.push(ToggleSubcanvasCommand(self, node_item))

    def _connect_edge_undo_tracking(self, edge: object) -> None:
        """Connect control point change tracking for an edge."""
        if hasattr(edge, "cp_changed_callback"):
            edge.cp_changed_callback = lambda: self._on_edge_cp_changed(edge)

    def _on_edge_cp_changed(
        self,
        edge: object,
    ) -> None:
        """Handle control point changes: push a ChangeControlPointsCommand."""
        saved = getattr(edge, "_saved_control_points", None)
        current = getattr(edge, "control_points", [])
        if saved is not None and saved != current:
            from app.commands.change_control_points_command import (
                ChangeControlPointsCommand,
            )
            self.undo_stack.push(
                ChangeControlPointsCommand(self, edge, list(saved), list(current))
            )

    def set_selection_mode(
        self,
        enabled: bool,
    ) -> None:
        """Enable/disable selection mode"""
        self.selection_mode = enabled
        if not enabled:
            scene = self.canvas.scene()
            if scene is not None:
                scene.clearSelection()
            self.selected_node = None
            self.selected_edge = None
            self.current_selection = None

    def on_selection_changed(self) -> None:
        """Handle selection changes considering subcanvases and edges"""
        scene = self.canvas.scene()
        if scene is None:
            self.selection_changed.emit(None)
            self.selected_node = None
            self.selected_edge = None
            self.current_selection = None
            return

        selected_items = scene.selectedItems()

        if not selected_items:
            self.selection_changed.emit(None)
            self.selected_node = None
            self.selected_edge = None
            self.current_selection = None
            return

        item = selected_items[0]

        if isinstance(item, BaseEdgeItem):
            print(f"Edge selected: {item}")
            self.edge_selected.emit(item)
            self.selected_edge = item
            self.selected_node = None
            self.current_selection = item
            self.selection_changed.emit(item)
            return

        if not isinstance(item, (BaseNodeItem, BaseTroposItem)):
            self.selection_changed.emit(None)
            self.selected_node = None
            self.selected_edge = None
            self.current_selection = None
            return

        old_selected_node = self.selected_node
        self.selected_node = item
        self.selected_edge = None
        self.current_selection = item

        if old_selected_node != item:
            print(f"CanvasController: node selection changed to {item}")
            self.node_selected.emit(item)

        if hasattr(item, "subcanvas_parent") and item.subcanvas_parent:
            parent_node = item.subcanvas_parent.parentItem()
            if isinstance(parent_node, BaseNodeItem):
                if not parent_node.is_subcanvas_visible():
                    parent_node.ensure_subcanvas_visible()

        self.selection_changed.emit(item)

    def update_node_properties(
        self,
        properties: PropertyMap,
    ) -> None:
        """Update properties of the selected node via undo command"""
        selection = self.current_selection
        if isinstance(selection, (BaseNodeItem, BaseTroposItem)):
            old_properties: PropertyMap = {}
            for key in properties:
                val = self._get_node_property(selection, key)
                if val is not None:
                    old_properties[key] = val

            cmd = ChangePropertyCommand(
                self,
                selection,
                old_properties,
                dict(properties),
            )
            self.undo_stack.push(cmd)

    def find_node_by_ui(
        self,
        ui_item: CanvasNodeItem,
    ) -> CanvasNodeItem | None:
        for node in self.nodes:
            if node is ui_item:
                return node
        return None
