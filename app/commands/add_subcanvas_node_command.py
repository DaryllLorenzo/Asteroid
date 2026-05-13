from typing import Any

from PyQt6.QtGui import QUndoCommand


class AddSubcanvasNodeCommand(QUndoCommand):
    def __init__(
        self,
        controller: Any,
        parent_node_item: Any,
        subcanvas: Any,
        item_type: str,
        local_x: float,
        local_y: float,
    ) -> None:
        super().__init__("Añadir nodo a subcanvas")
        self._controller = controller
        self._parent_node_item = parent_node_item
        self._subcanvas = subcanvas
        self._item_type = item_type
        self._local_x = local_x
        self._local_y = local_y
        self._child_node: Any = None

    def redo(self) -> None:
        if self._child_node is None:
            self._child_node = self._controller._add_to_subcanvas(
                self._parent_node_item,
                self._subcanvas,
                self._item_type,
                self._local_x,
                self._local_y,
            )
        else:
            self._restore_child()

    def undo(self) -> None:
        if self._child_node is None:
            return
        if hasattr(self._parent_node_item, "child_nodes"):
            if self._child_node in self._parent_node_item.child_nodes:
                self._parent_node_item.child_nodes.remove(self._child_node)
        self._controller._remove_node_clean(self._child_node)

    def _restore_child(self) -> None:
        child = self._child_node
        subcanvas = self._subcanvas

        child.setParentItem(subcanvas)
        child.subcanvas_parent = subcanvas
        child.setVisible(subcanvas.isVisible())

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

        if not hasattr(self._parent_node_item, "child_nodes"):
            self._parent_node_item.child_nodes = []
        if child not in self._parent_node_item.child_nodes:
            self._parent_node_item.child_nodes.append(child)
