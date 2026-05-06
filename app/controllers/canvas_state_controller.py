# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------
from PyQt6.QtGui import QKeySequence
from PyQt6.QtGui import QShortcut

from app.ui.components.base_edge_item import BaseEdgeItem


class CanvasStateController:
    @property
    def is_modified(self):
        return self._is_modified

    @is_modified.setter
    def is_modified(self, value):
        if self._is_modified != value:
            self._is_modified = value
            self.project_modified.emit(value)

    def mark_as_modified(self):
        """Mark project as modified"""
        self.is_modified = True

    def mark_as_saved(self, file_path=None):
        """Mark project as saved"""
        self.is_modified = False
        if file_path:
            self._current_file_path = file_path

    def _setup_delete_shortcut(self):
        """Setup keyboard shortcut to delete selected elements"""
        self.delete_shortcut = QShortcut(QKeySequence("Delete"), self.canvas)
        self.delete_shortcut.activated.connect(self.delete_selected_item)

        self.delete_shortcut2 = QShortcut(QKeySequence("Ctrl+D"), self.canvas)
        self.delete_shortcut2.activated.connect(self.delete_selected_item)

    def set_selection_mode(self, enabled):
        """Enable/disable selection mode"""
        self.selection_mode = enabled
        if not enabled:
            self.canvas.scene.clearSelection()
            self.selected_node = None
            self.selected_edge = None
            self.current_selection = None

    def on_selection_changed(self):
        """Handle selection changes considering subcanvases and edges"""
        selected_items = self.canvas.scene.selectedItems()

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

        old_selected_node = self.selected_node
        self.selected_node = item
        self.selected_edge = None
        self.current_selection = item

        if old_selected_node != item:
            print(f"CanvasController: node selection changed to {item}")
            self.node_selected.emit(item)

        if hasattr(item, "subcanvas_parent") and item.subcanvas_parent:
            parent_node = item.subcanvas_parent.parentItem()
            if parent_node and hasattr(parent_node, "subcanvas"):
                if not parent_node.is_subcanvas_visible():
                    parent_node.ensure_subcanvas_visible()

        self.selection_changed.emit(item)

    def update_node_properties(self, properties: dict):
        """Update properties of the selected node"""
        if self.current_selection and hasattr(
            self.current_selection, "update_properties"
        ):
            self.current_selection.update_properties(properties)
            self.current_selection.update()
            self.selected_node_properties_changed.emit(properties)
            self.mark_as_modified()

    def find_node_by_ui(self, ui_item):
        for node in self.nodes:
            if node is ui_item:
                return node
        return None
