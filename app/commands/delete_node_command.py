# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------

from typing import Any

from PyQt6.QtGui import QUndoCommand

from app.controller_types import CanvasNodeItem


class DeleteNodeCommand(QUndoCommand):
    """
    Delete Node Command.

    Methods:
        __init__: Initialize the instance.
        redo: Redo.
        undo: Undo.
    """

    def __init__(self, controller: Any, node_item: CanvasNodeItem) -> None:
        """
        Initialize the instance.

        Args:
            controller (Any): The controller.
            node_item (CanvasNodeItem): The node item.
        """
        super().__init__("Eliminar nodo")
        self._controller = controller
        self._node_item = node_item
        self._node_data: dict | None = None
        self._edges_data: list[dict] = []
        self._child_nodes_data: list[dict] = []
        self._composite_internal_node: CanvasNodeItem | None = None
        self._composite_internal_parent: Any = None
        self._composite_internal_data: dict | None = None

    def redo(self) -> None:
        """Redo."""
        if self._node_data is not None:
            self._do_delete()
            return
        self._collect_and_delete()

    def _collect_and_delete(self) -> None:
        """Collect And Delete."""
        self._node_data = self._node_item.get_serializable_properties()

        self._edges_data = []
        self._collect_edges_recursive(self._node_item)

        self._detect_composite_internal_node()

        self._child_nodes_data = self._collect_children(self._node_item)
        self._node_data["children"] = self._child_nodes_data

        self._do_delete()

    def _detect_composite_internal_node(self) -> None:
        """Detect Composite Internal Node."""
        if not hasattr(self._node_item, "_independent_model"):
            return
        if self._node_item._independent_model is None:
            return

        for other in list(self._controller.nodes):
            if other is self._node_item:
                continue
            if not hasattr(other, "model") or not hasattr(self._node_item, "model"):
                continue
            if other.model is self._node_item.model:
                if (
                    hasattr(other, "subcanvas_parent")
                    and other.subcanvas_parent is not None
                ):
                    self._composite_internal_node = other
                    self._composite_internal_parent = (
                        other.subcanvas_parent.parentItem()
                    )
                    self._composite_internal_data = other.get_serializable_properties()
                    self._collect_edges_recursive(other)
                    return

    def _collect_edges_recursive(self, node_item) -> None:
        """
        Collect Edges Recursive.

        Args:
            node_item: The node item.
        """
        for edge in list(self._controller.edges):
            if edge.source_node is node_item or edge.dest_node is node_item:
                if not any(d["edge"] is edge for d in self._edges_data):
                    self._edges_data.append(
                        {
                            "edge": edge,
                            "source": edge.source_node,
                            "dest": edge.dest_node,
                            "parent_item": edge.parentItem(),
                        }
                    )
        for child in getattr(node_item, "child_nodes", []):
            self._collect_edges_recursive(child)

    def _collect_children(self, parent_item) -> list[dict]:
        """
        Collect Children.

        Args:
            parent_item: The parent item.

        Returns:
            list[dict]: Collect Children.
        """
        children = []
        for child in getattr(parent_item, "child_nodes", []):
            child_data = child.get_serializable_properties()
            child_data["node"] = child
            child_data["children"] = self._collect_children(child)
            children.append(child_data)
        return children

    def _do_delete(self) -> None:
        """Do Delete."""
        for edge_data in self._edges_data:
            edge = edge_data["edge"]
            if edge.scene() is not None:
                edge.cleanup()
                edge.scene().removeItem(edge)
            if edge in self._controller.edges:
                self._controller.edges.remove(edge)

        if self._composite_internal_node is not None:
            parent = self._composite_internal_parent
            if parent is not None and hasattr(parent, "child_nodes"):
                if self._composite_internal_node in parent.child_nodes:
                    parent.child_nodes.remove(self._composite_internal_node)
            self._controller._remove_node_clean(self._composite_internal_node)

        self._delete_child_nodes(self._node_item)
        self._controller._remove_node_clean(self._node_item)

    def _delete_child_nodes(self, parent_item) -> None:
        """
        Delete Child Nodes.

        Args:
            parent_item: The parent item.
        """
        for child in getattr(parent_item, "child_nodes", []):
            self._controller._remove_node_clean(child)

    def _restore_child_nodes(self, parent_item, children_data) -> None:
        """
        Restore Child Nodes.

        Args:
            parent_item: The parent item.
            children_data: The children data.
        """
        subcanvas = getattr(parent_item, "subcanvas", None)
        for child_data in children_data:
            child = child_data.get("node")
            if child is None:
                continue
            if subcanvas is not None:
                child.setParentItem(subcanvas)
                child.subcanvas_parent = subcanvas
            scene = self._controller.canvas.scene()
            if scene is not None and child.scene() is None:
                scene.addItem(child)
            if child not in self._controller.nodes:
                self._controller.nodes.append(child)
            if hasattr(child, "properties_changed"):
                child.properties_changed.connect(
                    self._controller.on_node_properties_changed
                )
            if hasattr(child, "drag_finished"):
                child.drag_finished.connect(self._controller._on_node_drag_finished)
            if hasattr(child, "resize_finished"):
                child.resize_finished.connect(self._controller._on_node_resize_finished)
            if hasattr(child, "subcanvas_toggle_requested"):
                child.subcanvas_toggle_requested.connect(
                    self._controller._on_subcanvas_toggle_requested
                )
            if not hasattr(parent_item, "child_nodes"):
                parent_item.child_nodes = []
            if child not in parent_item.child_nodes:
                parent_item.child_nodes.append(child)

            self._restore_child_nodes(child, child_data.get("children", []))

    def _restore_edge(self, edge_data: dict) -> None:
        """
        Restore Edge.

        Args:
            edge_data (dict): The edge data.
        """
        edge = edge_data["edge"]
        parent = edge_data.get("parent_item")
        if edge.scene() is None:
            if parent is not None and parent.scene() is not None:
                edge.setParentItem(parent)
            else:
                scene = self._controller.canvas.scene()
                if scene is not None:
                    scene.addItem(edge)
        if edge not in self._controller.edges:
            self._controller.edges.append(edge)
        if hasattr(edge, "_connect_to_nodes"):
            edge._connect_to_nodes()
        if hasattr(self._controller, "_connect_edge_undo_tracking"):
            self._controller._connect_edge_undo_tracking(edge)
        edge.update_position()

    def undo(self) -> None:
        """Undo."""
        if self._node_data is None:
            return

        scene = self._controller.canvas.scene()
        if scene is not None and self._node_item.scene() is None:
            scene.addItem(self._node_item)
        if self._node_item not in self._controller.nodes:
            self._controller.nodes.append(self._node_item)

        if hasattr(self._node_item, "properties_changed"):
            self._node_item.properties_changed.connect(
                self._controller.on_node_properties_changed
            )
        if hasattr(self._node_item, "subcanvas_toggled"):
            self._node_item.subcanvas_toggled.connect(
                self._controller._on_subcanvas_toggled
            )
        if hasattr(self._node_item, "drag_finished"):
            self._node_item.drag_finished.connect(
                self._controller._on_node_drag_finished
            )
        if hasattr(self._node_item, "resize_finished"):
            self._node_item.resize_finished.connect(
                self._controller._on_node_resize_finished
            )
        if hasattr(self._node_item, "subcanvas_toggle_requested"):
            self._node_item.subcanvas_toggle_requested.connect(
                self._controller._on_subcanvas_toggle_requested
            )

        if self._node_data:
            self._node_item.update_properties(self._node_data)

        self._restore_child_nodes(self._node_item, self._child_nodes_data)

        if (
            self._composite_internal_node is not None
            and self._composite_internal_data is not None
        ):
            internal = self._composite_internal_node
            internal_parent = self._composite_internal_parent
            if scene is not None and internal.scene() is None:
                scene.addItem(internal)
            if internal not in self._controller.nodes:
                self._controller.nodes.append(internal)
            if hasattr(internal, "properties_changed"):
                internal.properties_changed.connect(
                    self._controller.on_node_properties_changed
                )
            if hasattr(internal, "drag_finished"):
                internal.drag_finished.connect(self._controller._on_node_drag_finished)
            if hasattr(internal, "resize_finished"):
                internal.resize_finished.connect(
                    self._controller._on_node_resize_finished
                )
            if hasattr(internal, "subcanvas_toggle_requested"):
                internal.subcanvas_toggle_requested.connect(
                    self._controller._on_subcanvas_toggle_requested
                )
            if internal_parent is not None:
                subcanvas = getattr(internal_parent, "subcanvas", None)
                if subcanvas is not None:
                    internal.setParentItem(subcanvas)
                    internal.subcanvas_parent = subcanvas
                if not hasattr(internal_parent, "child_nodes"):
                    internal_parent.child_nodes = []
                if internal not in internal_parent.child_nodes:
                    internal_parent.child_nodes.append(internal)

        for edge_data in self._edges_data:
            self._restore_edge(edge_data)
