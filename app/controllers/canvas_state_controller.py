# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------
from PyQt6.QtGui import QKeySequence
from PyQt6.QtGui import QShortcut

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
        self.is_modified = False
        if file_path:
            self._current_file_path = file_path

    def _setup_delete_shortcut(self) -> None:
        """Setup keyboard shortcut to delete selected elements"""
        self.delete_shortcut = QShortcut(QKeySequence("Delete"), self.canvas)
        self.delete_shortcut.activated.connect(self.delete_selected_item)

        self.delete_shortcut2 = QShortcut(QKeySequence("Ctrl+D"), self.canvas)
        self.delete_shortcut2.activated.connect(self.delete_selected_item)

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
        """Update properties of the selected node"""
        if self.current_selection and hasattr(
            self.current_selection, "update_properties"
        ):
            self.current_selection.update_properties(properties)
            self.current_selection.update()
            self.selected_node_properties_changed.emit(properties)
            self.mark_as_modified()

    def find_node_by_ui(
        self,
        ui_item: CanvasNodeItem,
    ) -> CanvasNodeItem | None:
        for node in self.nodes:
            if node is ui_item:
                return node
        return None
