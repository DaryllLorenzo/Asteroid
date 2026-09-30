# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------
import logging

from app.controller_types import CanvasNodeItem
from app.controllers._canvas_mixin import CanvasControllerMixin
from app.ui.components.base_edge_item import BaseEdgeItem
from app.ui.components.base_node_item import BaseNodeItem
from app.ui.components.base_tropos_item import BaseTroposItem
from app.ui.components.control_point_handle import ControlPointHandle

logger = logging.getLogger(__name__)


class CanvasDeletionController(CanvasControllerMixin):
    def delete_selected_item(self) -> None:
        scene = self.canvas.scene()
        if scene is None:
            return

        selected_items = scene.selectedItems()
        for item in selected_items:
            if isinstance(item, ControlPointHandle):
                self._delete_selected_control_point(item)
                return

        if self.selected_edge:
            self.delete_selected_edge()
        elif self.selected_node:
            self.delete_selected_node()
        else:
            logger.debug("No element selected for deletion")

    def _delete_selected_control_point(
        self,
        handle: ControlPointHandle,
    ) -> None:
        if not handle.parent_edge:
            return

        edge = handle.parent_edge
        try:
            index = edge.control_handles.index(handle)
            edge.remove_control_point(index)
            self.mark_as_modified()
            logger.debug("Control point removed from edge %s", edge)
        except ValueError:
            pass

    def delete_selected_node(self) -> None:
        if not self.selected_node:
            logger.debug("No node selected for deletion")
            return

        self.delete_node(self.selected_node)

    def delete_selected_edge(self) -> None:
        if not self.selected_edge:
            logger.debug("No edge selected for deletion")
            return

        logger.debug("Deleting edge: %s", self.selected_edge)
        self.delete_edge(self.selected_edge)

    def delete_node(
        self,
        node_to_delete: CanvasNodeItem,
    ) -> None:
        if node_to_delete not in self.nodes:
            if node_to_delete.scene():
                logger.debug("Deleting node directly from scene (not in list)")
                self._remove_node_from_scene(node_to_delete)
                return
            logger.warning("Node not found and not in scene: %s", node_to_delete)
            return

        logger.debug("Deleting node: %s", node_to_delete)

        edges_to_remove = []
        for edge in self.edges[:]:
            if edge.source_node == node_to_delete or edge.dest_node == node_to_delete:
                edges_to_remove.append(edge)

        for edge in edges_to_remove:
            self.delete_edge(edge)

        if hasattr(node_to_delete, "child_nodes") and node_to_delete.child_nodes:
            logger.debug("Deleting %d child nodes...", len(node_to_delete.child_nodes))
            child_nodes_copy = node_to_delete.child_nodes.copy()
            for child_node in child_nodes_copy:
                if isinstance(child_node, (BaseNodeItem, BaseTroposItem)):
                    self.delete_node(child_node)

        if hasattr(node_to_delete, "subcanvas") and node_to_delete.subcanvas:
            subcanvas_scene = node_to_delete.subcanvas.scene()
            node_scene = node_to_delete.scene()
            if subcanvas_scene is not None and node_scene is not None:
                node_scene.removeItem(node_to_delete.subcanvas)
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
        logger.debug("Node successfully deleted: %s", node_to_delete)

    def delete_edge(
        self,
        edge_to_delete: BaseEdgeItem,
    ) -> None:
        if edge_to_delete in self.edges:
            if hasattr(edge_to_delete, "cleanup"):
                edge_to_delete.cleanup()

            edge_scene = edge_to_delete.scene()
            if edge_scene is not None:
                edge_scene.removeItem(edge_to_delete)
            self.edges.remove(edge_to_delete)

            if edge_to_delete == self.selected_edge:
                self.selected_edge = None
                self.current_selection = None
                self.edge_selected.emit(None)
                self.selection_changed.emit(None)

            self.edge_deleted.emit(edge_to_delete)
            self.mark_as_modified()
            logger.debug("Edge deleted: %s", edge_to_delete)
        else:
            logger.warning("Edge not found in list: %s", edge_to_delete)

    def straighten_edge(
        self,
        edge: BaseEdgeItem,
    ) -> None:
        if edge and hasattr(edge, "clear_control_points"):
            edge.clear_control_points()
            self.mark_as_modified()
            logger.debug("Edge straightened: %s", edge)

    def _remove_node_clean(
        self,
        node: CanvasNodeItem,
    ) -> None:
        node_scene = node.scene()
        if node_scene is not None:
            node_scene.removeItem(node)
        if node in self.nodes:
            self.nodes.remove(node)

        if node == self.selected_node:
            self.selected_node = None
            self.current_selection = None
            self.node_selected.emit(None)
            self.selection_changed.emit(None)

    def _collect_edges_for_node(
        self,
        node_item: CanvasNodeItem,
    ) -> list[dict]:
        edges_data = []
        for edge in list(self.edges):
            if edge.source_node is node_item or edge.dest_node is node_item:
                edges_data.append(
                    {
                        "edge": edge,
                        "source": edge.source_node,
                        "dest": edge.dest_node,
                    }
                )
        return edges_data

    def _remove_node_from_scene(
        self,
        node: CanvasNodeItem,
    ) -> None:
        if node.scene():
            scene = node.scene()
            if scene is not None:
                scene.removeItem(node)

    def clear_canvas(self) -> None:
        if hasattr(self, "undo_stack"):
            self.undo_stack.clear()
        self.selected_node = None
        self.selected_edge = None
        self.current_selection = None

        for edge in self.edges[:]:
            scene = edge.scene()
            if scene is not None:
                scene.removeItem(edge)
        self.edges.clear()

        for node in self.nodes[:]:
            scene = node.scene()
            if scene is not None:
                scene.removeItem(node)
        self.nodes.clear()

        scene = self.canvas.scene()
        if scene is not None:
            scene.clearSelection()
        self.is_modified = False
        self._current_file_path = None
        logger.debug("Canvas cleared")
