from typing import Any

from PyQt6.QtGui import QUndoCommand

from app.controller_types import CanvasNodeItem


class AddNodeCommand(QUndoCommand):
    def __init__(
        self,
        controller: Any,
        node_type: str,
        x: float,
        y: float,
    ) -> None:
        super().__init__("Añadir nodo")
        self._controller = controller
        self._node_type = node_type
        self._x = x
        self._y = y
        self._node_item: CanvasNodeItem | None = None
        self._node_data: dict | None = None
        self._edges_data: list[dict] = []

    def redo(self) -> None:
        if self._node_item is None:
            self._node_item = self._controller.add_node(
                self._node_type, self._x, self._y
            )
            if self._node_item and hasattr(self._node_item, "drag_finished"):
                self._node_item.drag_finished.connect(
                    self._controller._on_node_drag_finished
                )
        else:
            self._controller._restore_node(self._node_item)
            if self._node_data:
                self._node_item.update_properties(self._node_data)
            for edge_data in self._edges_data:
                self._restore_edge(edge_data)
            self._restore_children(self._node_item, self._node_data)

    def _restore_edge(self, edge_data: dict) -> None:
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

    def _restore_children(self, parent_item, data) -> None:
        if data is None:
            return
        children_data = data.get("children", [])
        for child_data in children_data:
            child = child_data.get("node")
            if child is not None and child.scene() is None:
                subcanvas = getattr(parent_item, "subcanvas", None)
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
                    child.resize_finished.connect(
                        self._controller._on_node_resize_finished
                    )
                if hasattr(child, "subcanvas_toggle_requested"):
                    child.subcanvas_toggle_requested.connect(
                        self._controller._on_subcanvas_toggle_requested
                    )
                self._restore_children(child, child_data)

    def undo(self) -> None:
        if self._node_item is None:
            return

        self._node_data = self._node_item.get_serializable_properties()
        self._node_data["children"] = self._collect_children_data(self._node_item)

        self._edges_data = []
        for edge in list(self._controller.edges):
            if edge.source_node is self._node_item or edge.dest_node is self._node_item:
                edge.cleanup()
                self._edges_data.append(
                    {
                        "edge": edge,
                        "parent_item": edge.parentItem(),
                    }
                )
                edge_scene = edge.scene()
                if edge_scene is not None:
                    edge_scene.removeItem(edge)
                self._controller.edges.remove(edge)

        self._controller._remove_node_clean(self._node_item)

    def _collect_children_data(self, parent_item) -> list[dict]:
        children = []
        for child in getattr(parent_item, "child_nodes", []):
            child_data = child.get_serializable_properties()
            child_data["node"] = child
            child_data["children"] = self._collect_children_data(child)
            children.append(child_data)
        return children
