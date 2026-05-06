# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------
from app.ui.components.control_point_handle import ControlPointHandle


class CanvasDeletionController:
    def delete_selected_item(self):
        """Delete currently selected item (node, edge, or control point).
        Priority: control point > edge > node.
        """
        selected_items = self.canvas.scene.selectedItems()
        for item in selected_items:
            if isinstance(item, ControlPointHandle):
                self._delete_selected_control_point(item)
                return

        if self.selected_edge:
            self.delete_selected_edge()
        elif self.selected_node:
            self.delete_selected_node()
        else:
            print("No element selected for deletion")

    def _delete_selected_control_point(self, handle: ControlPointHandle):
        """Delete a specific control point from an edge"""
        if not handle.parent_edge:
            return

        edge = handle.parent_edge
        try:
            index = edge.control_handles.index(handle)
            edge.remove_control_point(index)
            self.mark_as_modified()
            print(f"Control point removed from edge {edge}")
        except ValueError:
            pass

    def delete_selected_node(self):
        """Delete currently selected node"""
        if not self.selected_node:
            print("No node selected for deletion")
            return

        print(f"Deleting node: {self.selected_node}")
        self.delete_node(self.selected_node)

    def delete_selected_edge(self):
        """Delete currently selected edge"""
        if not self.selected_edge:
            print("No edge selected for deletion")
            return

        print(f"Deleting edge: {self.selected_edge}")
        self.delete_edge(self.selected_edge)

    def delete_node(self, node_to_delete):
        """Delete a specific node and all its connections"""
        if node_to_delete not in self.nodes:
            if node_to_delete.scene():
                print("Deleting node directly from scene (not in list)")
                self._remove_node_from_scene(node_to_delete)
                return
            print(f"Node not found and not in scene: {node_to_delete}")
            return

        print(f"Deleting node: {node_to_delete}")

        edges_to_remove = []
        for edge in self.edges[:]:
            if edge.source_node == node_to_delete or edge.dest_node == node_to_delete:
                edges_to_remove.append(edge)

        for edge in edges_to_remove:
            self.delete_edge(edge)

        if hasattr(node_to_delete, "child_nodes") and node_to_delete.child_nodes:
            print(f"Deleting {len(node_to_delete.child_nodes)} child nodes...")
            child_nodes_copy = node_to_delete.child_nodes.copy()
            for child_node in child_nodes_copy:
                self.delete_node(child_node)

        if hasattr(node_to_delete, "subcanvas") and node_to_delete.subcanvas:
            if node_to_delete.subcanvas.scene():
                node_to_delete.scene().removeItem(node_to_delete.subcanvas)
            node_to_delete.subcanvas = None

        self._remove_node_from_scene(node_to_delete)

        if node_to_delete in self.nodes:
            self.nodes.remove(node_to_delete)

        if node_to_delete == self.selected_node:
            self.selected_node = None
            self.current_selection = None
            self.node_selected.emit(None)
            self.selection_changed.emit(None)

        self.node_deleted.emit(node_to_delete)
        self.mark_as_modified()
        print(f"Node successfully deleted: {node_to_delete}")

    def delete_edge(self, edge_to_delete):
        """Delete a specific edge"""
        if edge_to_delete in self.edges:
            if hasattr(edge_to_delete, "cleanup"):
                edge_to_delete.cleanup()

            if edge_to_delete.scene():
                edge_to_delete.scene().removeItem(edge_to_delete)
            self.edges.remove(edge_to_delete)

            if edge_to_delete == self.selected_edge:
                self.selected_edge = None
                self.current_selection = None
                self.edge_selected.emit(None)
                self.selection_changed.emit(None)

            self.edge_deleted.emit(edge_to_delete)
            self.mark_as_modified()
            print(f"Edge deleted: {edge_to_delete}")
        else:
            print(f"Edge not found in list: {edge_to_delete}")

    def straighten_edge(self, edge):
        """Straighten an edge by removing all control points."""
        if edge and hasattr(edge, "clear_control_points"):
            edge.clear_control_points()
            self.mark_as_modified()
            print(f"Edge straightened: {edge}")

    def _remove_node_from_scene(self, node):
        """Safely remove a node from the scene"""
        if node.scene():
            node.scene().removeItem(node)

    def clear_canvas(self):
        """Clear canvas completely"""
        self.selected_node = None
        self.selected_edge = None
        self.current_selection = None

        for edge in self.edges[:]:
            if edge.scene():
                edge.scene().removeItem(edge)
        self.edges.clear()

        for node in self.nodes[:]:
            if node.scene():
                node.scene().removeItem(node)
        self.nodes.clear()

        self.canvas.scene.clearSelection()
        self.is_modified = False
        self._current_file_path = None
        print("Canvas cleared")
