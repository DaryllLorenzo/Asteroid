from typing import Any

from PyQt6.QtGui import QUndoCommand


class AddCompositeDependencyCommand(QUndoCommand):
    """
    Add Composite Dependency Command.

    Methods:
        __init__: Initialize the instance.
        redo: Redo.
        undo: Undo.
    """

    def __init__(self, controller: Any) -> None:
        """
        Initialize the instance.

        Args:
            controller (Any): The controller.
        """
        super().__init__("Crear dependencia compuesta")
        self._controller = controller
        self._mid_node: Any = None
        self._internal_node: Any = None
        self._e1: Any = None
        self._e2: Any = None
        nodes_for_arrow = getattr(controller, "selected_nodes_for_arrow", [])
        self._src: Any = nodes_for_arrow[0] if len(nodes_for_arrow) >= 1 else None
        self._dst: Any = nodes_for_arrow[1] if len(nodes_for_arrow) >= 2 else None

    def redo(self) -> None:
        """Redo."""
        if self._mid_node is not None:
            self._restore_all()
            return
        result = self._controller.create_composite_dependency()
        if result is None or len(result) < 4:
            return
        self._mid_node, self._internal_node, self._e1, self._e2 = result

    def _restore_all(self) -> None:
        """Restore All."""
        ctrl = self._controller
        scene = ctrl.canvas.scene()
        if scene is None:
            return

        if self._mid_node is not None and self._mid_node.scene() is None:
            scene.addItem(self._mid_node)
        if self._mid_node not in ctrl.nodes:
            ctrl.nodes.append(self._mid_node)

        if self._internal_node is not None and self._internal_node.scene() is None:
            scene.addItem(self._internal_node)
        if self._internal_node not in ctrl.nodes:
            ctrl.nodes.append(self._internal_node)
        if self._dst is not None:
            subcanvas = getattr(self._dst, "subcanvas", None)
            if subcanvas is not None:
                self._internal_node.setParentItem(subcanvas)
                self._internal_node.subcanvas_parent = subcanvas
            if not hasattr(self._dst, "child_nodes"):
                self._dst.child_nodes = []
            if self._internal_node not in self._dst.child_nodes:
                self._dst.child_nodes.append(self._internal_node)

        for edge in (self._e1, self._e2):
            if edge is not None and edge.scene() is None:
                scene.addItem(edge)
            if edge is not None and edge not in ctrl.edges:
                ctrl.edges.append(edge)
            if hasattr(edge, "_connect_to_nodes"):
                edge._connect_to_nodes()
            if hasattr(self._controller, "_connect_edge_undo_tracking"):
                self._controller._connect_edge_undo_tracking(edge)
            edge.update_position()

    def undo(self) -> None:
        """Undo."""
        ctrl = self._controller

        for edge in (self._e1, self._e2):
            if edge is not None and edge in ctrl.edges:
                if hasattr(edge, "cleanup"):
                    edge.cleanup()
                edge_scene = edge.scene()
                if edge_scene is not None:
                    edge_scene.removeItem(edge)
                ctrl.edges.remove(edge)

        if self._internal_node is not None:
            if self._dst is not None and hasattr(self._dst, "child_nodes"):
                if self._internal_node in self._dst.child_nodes:
                    self._dst.child_nodes.remove(self._internal_node)
            ctrl._remove_node_clean(self._internal_node)

        if self._mid_node is not None:
            ctrl._remove_node_clean(self._mid_node)
