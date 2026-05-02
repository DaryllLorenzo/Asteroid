# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------
from functools import partial
import json

from PyQt6.QtCore import QObject
from PyQt6.QtCore import QPointF
from PyQt6.QtCore import Qt
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QKeySequence
from PyQt6.QtGui import QPainter
from PyQt6.QtGui import QPixmap
from PyQt6.QtGui import QShortcut
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtWidgets import QMessageBox

from app.core.models.composite_model_wrapper import CompositeModelWrapper
from app.core.models.tropos_element.hard_goal import HardGoal
from app.core.models.tropos_element.plan import Plan
from app.core.models.tropos_element.resource import Resource
from app.core.models.tropos_element.soft_goal import SoftGoal
from app.ui.components.base_edge_item import BaseEdgeItem
from app.ui.components.control_point_handle import ControlPointHandle
from app.ui.components.dependency_item.and_decomposition_edge_item import (
    AndDecompositionArrowItem,
)
from app.ui.components.dependency_item.contribution_edge_item import (
    ContributionArrowItem,
)
from app.ui.components.dependency_item.dashed_edge_item import DashedArrowItem
from app.ui.components.dependency_item.dependency_link_edge_item import (
    DependencyLinkArrowItem,
)
from app.ui.components.dependency_item.means_end_edge_item import MeansEndArrowItem
from app.ui.components.dependency_item.or_decomposition_edge_item import (
    OrDecompositionArrowItem,
)
from app.ui.components.dependency_item.simple_edge_item import SimpleArrowItem
from app.ui.components.dependency_item.why_link_edge_item import WhyLinkArrowItem
from app.ui.components.entity_item.actor_node_item import ActorNodeItem
from app.ui.components.entity_item.agent_node_item import AgentNodeItem
from app.ui.components.tropos_element_item.hard_goal_item import HardGoalNodeItem
from app.ui.components.tropos_element_item.plan_item import PlanNodeItem
from app.ui.components.tropos_element_item.resource_item import ResourceNodeItem
from app.ui.components.tropos_element_item.soft_goal_item import SoftGoalNodeItem
from app.utils.astr_format import AstrFormat

_NODE_MAP = {
    "actor": ActorNodeItem,
    "agent": AgentNodeItem,
    "hard_goal": HardGoalNodeItem,
    "soft_goal": SoftGoalNodeItem,
    "plan": PlanNodeItem,
    "resource": ResourceNodeItem,
}

_MODEL_MAP = {
    "hard_goal": HardGoal,
    "soft_goal": SoftGoal,
    "plan": Plan,
    "resource": Resource,
}

_ARROW_TYPES = {
    "simple": SimpleArrowItem,
    "dashed": DashedArrowItem,
    "dependency_link": DependencyLinkArrowItem,
    "why_link": WhyLinkArrowItem,
    "or_decomposition": OrDecompositionArrowItem,
    "and_decomposition": AndDecompositionArrowItem,
    "contribution": ContributionArrowItem,
    "means_end": MeansEndArrowItem,
}


class CanvasController(QObject):
    node_selected = pyqtSignal(object)
    selected_node_properties_changed = pyqtSignal(dict)
    node_deleted = pyqtSignal(object)
    edge_selected = pyqtSignal(object)
    edge_deleted = pyqtSignal(object)
    selection_changed = pyqtSignal(object)
    project_modified = pyqtSignal(bool)

    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        self.nodes = []
        self.edges = []

        # Arrow mode
        self.arrow_mode = False
        self.selected_arrow_type = None
        self.selected_nodes_for_arrow = []

        # Composite mode
        self.composite_mode = False
        self.composite_node_type = None

        self._current_subcanvas = None

        # Selection mode
        self.selection_mode = False
        self.selected_node = None
        self.selected_edge = None
        self.current_selection = None

        self._subcanvas_handlers: dict[object, tuple[object, callable, callable]] = {}

        # Project state tracking
        self._current_file_path = None
        self._is_modified = False

        # Connect signals
        self.canvas.node_dropped.connect(self.add_node)
        self.canvas.arrow_dropped.connect(self.start_arrow_mode)
        self.canvas.node_clicked.connect(self.handle_node_click)
        self.canvas.scene.selectionChanged.connect(self.on_selection_changed)

        # Setup keyboard shortcuts for deletion
        self._setup_delete_shortcut()

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

        # Check if it is an edge
        if isinstance(item, BaseEdgeItem):
            print(f"Edge selected: {item}")
            self.edge_selected.emit(item)
            self.selected_edge = item
            self.selected_node = None
            self.current_selection = item
            self.selection_changed.emit(item)
            return

        # For nodes: update reference before emitting signals
        old_selected_node = self.selected_node
        self.selected_node = item
        self.selected_edge = None
        self.current_selection = item

        # Only emit node_selected if node actually changed
        if old_selected_node != item:
            print(f"CanvasController: node selection changed to {item}")
            self.node_selected.emit(item)

        # Check if node is inside a subcanvas
        if hasattr(item, "subcanvas_parent") and item.subcanvas_parent:
            parent_node = item.subcanvas_parent.parentItem()
            if parent_node and hasattr(parent_node, "subcanvas"):
                if not parent_node.is_subcanvas_visible():
                    parent_node.ensure_subcanvas_visible()

        # Always emit selection_changed to notify UI
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

    def add_node(self, node_type: str, x: float, y: float):
        NodeClass = _NODE_MAP.get(node_type)
        if NodeClass is None:
            return None

        node_item = NodeClass(0, 0)
        node_item.setPos(x, y)

        if hasattr(node_item, "model"):
            node_item.model.x = x
            node_item.model.y = y

        self.canvas.scene.addItem(node_item)
        self.nodes.append(node_item)

        if hasattr(node_item, "properties_changed"):
            node_item.properties_changed.connect(self.on_node_properties_changed)
        else:
            print(f"Warning: node {node_type} lacks properties_changed signal")

        if hasattr(node_item, "subcanvas_toggled"):
            node_item.subcanvas_toggled.connect(self._on_subcanvas_toggled)

        self.mark_as_modified()
        return node_item

    def on_node_properties_changed(self, node_item, properties):
        """Handle property changes emitted by nodes"""
        if node_item == self.selected_node:
            self.selected_node_properties_changed.emit(properties)

        if node_item == self.selected_node or (
            hasattr(node_item, "_resizing") and node_item._resizing
        ):
            self.selected_node_properties_changed.emit(properties)

        self.mark_as_modified()

    def start_arrow_mode(self, arrow_type: str):
        if arrow_type not in _ARROW_TYPES:
            return
        self._reset_modes()
        self.arrow_mode = True
        self.selected_arrow_type = arrow_type
        print(f"CanvasController: start global arrow mode '{arrow_type}'")

    def start_composite_dependency_mode(self, node_type: str):
        if node_type not in _NODE_MAP:
            print(f"CanvasController: unknown composite node_type '{node_type}'")
            return
        self._reset_modes()
        self.composite_mode = True
        self.composite_node_type = node_type
        self.selected_nodes_for_arrow = []
        print(
            f"CanvasController: start composite mode for '{node_type}'. "
            f"Click two Actor/Agent nodes."
        )

    def _reset_modes(self):
        self.arrow_mode = False
        self.selected_arrow_type = None
        self.selected_nodes_for_arrow = []
        self.composite_mode = False
        self.composite_node_type = None
        self._current_subcanvas = None

    def handle_node_click(self, node_item):
        if self.selection_mode:
            return

        if isinstance(node_item, BaseEdgeItem):
            node_item = node_item.source_node

        if self.composite_mode:
            self._handle_composite_mode_click(node_item)
            return

        if self.arrow_mode:
            self._handle_arrow_mode_click(node_item)

    def _handle_composite_mode_click(self, node_item):
        node = self._find_parent_actor_agent(node_item)
        if node is None:
            print("CanvasController: composite mode only accepts Actor/Agent; ignored.")
            return

        if node not in self.selected_nodes_for_arrow:
            self.selected_nodes_for_arrow.append(node)
            node.setSelected(True)

        if len(self.selected_nodes_for_arrow) == 2:
            self.create_composite_dependency()

    def _find_parent_actor_agent(self, node_item):
        node = node_item
        while node is not None and not isinstance(node, (ActorNodeItem, AgentNodeItem)):
            node = node.parentItem()
        return node

    def _handle_arrow_mode_click(self, node_item):
        node_subcanvas = getattr(node_item, "subcanvas_parent", None)
        if self._current_subcanvas:
            if node_subcanvas is not self._current_subcanvas:
                print("CanvasController: node not in current subcanvas, ignored")
                return

        if node_item not in self.selected_nodes_for_arrow:
            self.selected_nodes_for_arrow.append(node_item)
            node_item.setSelected(True)

        if len(self.selected_nodes_for_arrow) == 2:
            self.create_arrow()

    def _start_subarrow_mode(self, parent_node_item, subcanvas, arrow_type: str):
        if arrow_type not in _ARROW_TYPES:
            return
        self._reset_modes()
        self.arrow_mode = True
        self.selected_arrow_type = arrow_type
        self.selected_nodes_for_arrow = []
        self._current_subcanvas = subcanvas
        print(f"CanvasController: start subarrow mode '{arrow_type}' in {subcanvas}")

    def create_arrow(self):
        if len(self.selected_nodes_for_arrow) != 2:
            return None

        src, dst = self.selected_nodes_for_arrow
        ArrowClass = _ARROW_TYPES.get(self.selected_arrow_type)
        if ArrowClass is None:
            return None

        edge_item = ArrowClass(src, dst)

        if self._current_subcanvas:
            edge_item.setParentItem(self._current_subcanvas)
            edge_item.update_position()
            print(f"Edge created inside subcanvas: {self._current_subcanvas}")
        else:
            self.canvas.scene.addItem(edge_item)

        self.edges.append(edge_item)
        self._reset_modes()
        for n in self.nodes:
            n.setSelected(False)

        self.mark_as_modified()
        return edge_item

    def create_composite_dependency(self):
        if len(self.selected_nodes_for_arrow) != 2 or not self.composite_node_type:
            return None

        src, dst = self.selected_nodes_for_arrow
        NodeClass = _NODE_MAP[self.composite_node_type]
        ModelClass = _MODEL_MAP.get(self.composite_node_type)

        if not ModelClass:
            print(f"No model found for type '{self.composite_node_type}'")
            return None

        mid_x = (src.pos().x() + dst.pos().x()) / 2.0
        mid_y = (src.pos().y() + dst.pos().y()) / 2.0

        external_model = ModelClass(0, 0)
        external_model.x = mid_x
        external_model.y = mid_y

        internal_model = ModelClass(0, 0)
        internal_model.position_in_subcanvas_x = 0.6
        internal_model.position_in_subcanvas_y = 0.0

        wrapper = CompositeModelWrapper(external_model, internal_model)

        def on_model_changed(prop_name, value):
            mid_node.update()
            if hasattr(internal_node, "update"):
                internal_node.update()
            mid_node.properties_changed.emit(mid_node, {prop_name: value})

        wrapper.add_change_callback(on_model_changed)

        mid_node = NodeClass(0, 0)
        mid_node.setPos(mid_x, mid_y)
        mid_node.model = wrapper
        mid_node._independent_model = external_model
        self.canvas.scene.addItem(mid_node)
        self.nodes.append(mid_node)

        internal_node = NodeClass(0, 0)
        internal_node.model = wrapper
        internal_node._independent_model = internal_model

        e1 = DependencyLinkArrowItem(src, mid_node)
        e2 = DependencyLinkArrowItem(mid_node, dst)
        self.canvas.scene.addItem(e1)
        self.canvas.scene.addItem(e2)
        self.edges.extend([e1, e2])

        subcanvas = None
        if hasattr(dst, "prepare_subcanvas_for_internal_use"):
            subcanvas = dst.prepare_subcanvas_for_internal_use()
        else:
            print(
                "Destination node does not support subcanvas; "
                "internal insertion skipped."
            )

        if subcanvas:
            internal_node.setParentItem(subcanvas)
            offset_x = subcanvas.radius * 0.6
            offset_y = 0
            internal_node.setPos(offset_x, offset_y)
            internal_node.setVisible(True)
            internal_node.subcanvas_parent = subcanvas

            self.nodes.append(internal_node)

            if not hasattr(dst, "child_nodes"):
                dst.child_nodes = []
            dst.child_nodes.append(internal_node)

            print(
                f"Composite: node '{self.composite_node_type}' added to "
                f"{dst} subcanvas at ({offset_x:.1f}, {offset_y:.1f})"
            )

        for node in self.selected_nodes_for_arrow:
            node.setSelected(False)

        self._reset_modes()
        self.mark_as_modified()
        return (mid_node, e1, e2)

    def _on_subcanvas_toggled(self, parent_node_item, subcanvas):
        if subcanvas is None:
            stored = self._subcanvas_handlers.pop(parent_node_item, None)
            if stored:
                prev_subcanvas, handler_node, handler_arrow = stored
                try:
                    prev_subcanvas.subnode_dropped.disconnect(handler_node)
                    prev_subcanvas.subarrow_dropped.disconnect(handler_arrow)
                except Exception:
                    pass
            return

        stored = self._subcanvas_handlers.get(parent_node_item)
        if stored:
            prev_subcanvas, handler_node, handler_arrow = stored
            if prev_subcanvas is subcanvas:
                return
            try:
                prev_subcanvas.subnode_dropped.disconnect(handler_node)
                prev_subcanvas.subarrow_dropped.disconnect(handler_arrow)
            except Exception:
                pass

        handler_node = partial(self._add_to_subcanvas, parent_node_item, subcanvas)
        handler_arrow = partial(self._start_subarrow_mode, parent_node_item, subcanvas)

        subcanvas.subnode_dropped.connect(handler_node)
        subcanvas.subarrow_dropped.connect(handler_arrow)
        self._subcanvas_handlers[parent_node_item] = (
            subcanvas,
            handler_node,
            handler_arrow,
        )

        try:
            subcanvas.setZValue(parent_node_item.zValue() - 1)
        except Exception:
            pass

    def _add_to_subcanvas(
        self,
        parent_node_item,
        subcanvas,
        item_type: str,
        local_x: float,
        local_y: float,
    ):
        NodeClass = _NODE_MAP.get(item_type)
        if NodeClass is None:
            return None

        child = NodeClass(0, 0, radius=20)
        if child.scene() is not None and child.parentItem() is None:
            child.scene().removeItem(child)

        child.setParentItem(subcanvas)
        child.setPos(local_x, local_y)
        child.setVisible(subcanvas.isVisible())
        child.subcanvas_parent = subcanvas

        self.nodes.append(child)

        if hasattr(child, "properties_changed"):
            child.properties_changed.connect(self.on_node_properties_changed)
        else:
            print(f"Warning: internal node {item_type} lacks properties_changed signal")

        if not hasattr(parent_node_item, "child_nodes"):
            parent_node_item.child_nodes = []
        parent_node_item.child_nodes.append(child)

        self.mark_as_modified()
        return child

    def find_node_by_ui(self, ui_item):
        for n in self.nodes:
            if n is ui_item:
                return n
        return None

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
            else:
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

    def export_to_astr(self, filename: str = None) -> bool:
        """Export current canvas state to .astr file"""
        try:
            if not filename:
                filename, _ = QFileDialog.getSaveFileName(
                    self.canvas,
                    "Export as .astr",
                    "",
                    "Asteroid Files (*.astr)",
                )
                if not filename:
                    return False

                if not filename.endswith(".astr"):
                    filename += ".astr"

            scene_data = AstrFormat.serialize_scene(self.nodes, self.edges)

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(scene_data, f, indent=2, ensure_ascii=False)

            print(f"Project exported successfully: {filename}")
            self.mark_as_saved(filename)
            return True

        except Exception as e:
            print(f"Error exporting project: {e}")
            QMessageBox.critical(
                self.canvas, "Error", f"Could not export project:\n{e}"
            )
            return False

    def import_from_astr(self, filename: str = None) -> bool:
        """Import project from .astr file"""
        try:
            if not filename:
                filename, _ = QFileDialog.getOpenFileName(
                    self.canvas, "Load .astr project", "", "Asteroid Files (*.astr)"
                )
                if not filename:
                    return False

            print(f"Loading project from: {filename}")

            with open(filename, encoding="utf-8") as f:
                scene_data = json.load(f)

            print(
                f"Project contains: {len(scene_data.get('nodes', []))} nodes, "
                f"{len(scene_data.get('edges', []))} edges"
            )

            self.clear_canvas()

            node_map = {}
            parent_child_map = {}

            for node_data in scene_data.get("nodes", []):
                print(f"Processing node {node_data['id']} of type {node_data['type']}")
                node = self._create_node_from_data(node_data)
                if node:
                    node_map[node_data["id"]] = node
                    parent_id = node_data.get("parent_id")
                    if parent_id is not None:
                        if parent_id not in parent_child_map:
                            parent_child_map[parent_id] = []
                        parent_child_map[parent_id].append(node_data["id"])

            for parent_id, child_ids in parent_child_map.items():
                parent_node = node_map.get(parent_id)
                if parent_node and hasattr(parent_node, "subcanvas"):
                    print(
                        f"Moving {len(child_ids)} nodes to subcanvas "
                        f"of node {parent_id}"
                    )
                    for child_id in child_ids:
                        child_node = node_map.get(child_id)
                        if child_node:
                            self._move_node_to_subcanvas(child_node, parent_node)

            edge_count = 0
            edge_parent_map = {}

            for edge_data in scene_data.get("edges", []):
                edge = self._create_edge_from_data(edge_data, node_map)
                if edge:
                    edge_count += 1
                    parent_id = edge_data.get("parent_id")
                    if parent_id is not None:
                        edge_parent_map[edge] = parent_id

            for edge, parent_id in edge_parent_map.items():
                parent_node = node_map.get(parent_id)
                if parent_node and hasattr(parent_node, "subcanvas"):
                    self._move_edge_to_subcanvas(edge, parent_node)

            composite_nodes = {}
            for node_data in scene_data.get("nodes", []):
                model_props = node_data.get("model_properties", {})
                if model_props.get("is_composite", False):
                    parent_id = node_data.get("parent_id")
                    if parent_id is None:
                        composite_nodes[node_data["id"]] = node_data

            linked_internal_nodes = set()

            for node_id, node_data in composite_nodes.items():
                external_node = node_map.get(node_id)
                if not external_node:
                    continue

                model_props = node_data.get("model_properties", {})
                target_node = None
                for edge in self.edges:
                    if edge.source_node == external_node:
                        target_node = edge.dest_node
                        break

                if not target_node:
                    print(f"No outgoing edge found for composite node {node_id}")
                    continue

                if hasattr(target_node, "subcanvas") and target_node.subcanvas:
                    internal_node = None
                    expected_x = target_node.subcanvas.radius * float(
                        model_props.get("internal_position_in_subcanvas_x", 0.6)
                    )
                    expected_y = target_node.subcanvas.radius * float(
                        model_props.get("internal_position_in_subcanvas_y", 0.0)
                    )

                    candidates = []
                    for child in target_node.subcanvas.childItems():
                        if id(child) in linked_internal_nodes:
                            continue
                        if isinstance(child, type(external_node)) and hasattr(
                            child, "model"
                        ):
                            candidates.append(child)

                    if len(candidates) == 1:
                        internal_node = candidates[0]
                    elif len(candidates) > 1:
                        min_dist = float("inf")
                        for candidate in candidates:
                            dist = abs(candidate.pos().x() - expected_x) + abs(
                                candidate.pos().y() - expected_y
                            )
                            if dist < min_dist:
                                min_dist = dist
                                internal_node = candidate
                    else:
                        print(
                            f"No internal nodes of type "
                            f"{type(external_node).__name__} found in "
                            f"subcanvas of {target_node}"
                        )

                    if internal_node:
                        linked_internal_nodes.add(id(internal_node))
                        ModelClass = _MODEL_MAP.get(node_data["type"])
                        if ModelClass:
                            internal_radius = (
                                internal_node._independent_model.radius
                                if hasattr(internal_node, "_independent_model")
                                else getattr(internal_node.model, "radius", 50)
                            )

                            new_internal_model = ModelClass(0, 0)
                            new_internal_model.position_in_subcanvas_x = float(
                                model_props.get("internal_position_in_subcanvas_x", 0.6)
                            )
                            new_internal_model.position_in_subcanvas_y = float(
                                model_props.get("internal_position_in_subcanvas_y", 0.0)
                            )
                            new_internal_model.radius = internal_radius

                            external_model = external_node.model
                            wrapper = CompositeModelWrapper(
                                external_model, new_internal_model
                            )

                            external_node.model = wrapper
                            external_node._independent_model = external_model
                            internal_node.model = wrapper
                            internal_node._independent_model = new_internal_model

                            wrapper.label = model_props.get("label", "")
                            wrapper.color = model_props.get("color", "#3498db")
                            wrapper.border_color = model_props.get(
                                "border_color", "#2980b9"
                            )
                            wrapper.text_color = model_props.get(
                                "text_color", "#ffffff"
                            )

                            external_model.radius = float(model_props.get("radius", 50))

                            external_node.update()
                            internal_node.update()

                            def on_external_changed(prop_name, value, node):
                                node.update()
                                node.properties_changed.emit(node, {prop_name: value})

                            def on_internal_changed(prop_name, value, node):
                                node.update()

                            callback_ext = on_external_changed
                            callback_int = on_internal_changed

                            ext_n = external_node
                            int_n = internal_node

                            wrapper.add_change_callback(
                                lambda p, v, cb=callback_ext, n=ext_n: cb(p, v, n)
                            )
                            wrapper.add_change_callback(
                                lambda p, v, cb=callback_int, n=int_n: cb(p, v, n)
                            )
                    else:
                        print(f"No internal node found in subcanvas of {target_node}")
                else:
                    print(f"Target {target_node} has no subcanvas")

            print(f"Project loaded successfully: {filename}")
            print(f"Summary: {len(node_map)} nodes, {edge_count} edges reconstructed")

            self.mark_as_saved(filename)
            return True

        except Exception as e:
            print(f"Error loading project: {e}")
            import traceback

            traceback.print_exc()
            QMessageBox.critical(self.canvas, "Error", f"Could not load project:\n{e}")
            return False

    def _move_node_to_subcanvas(self, child_node, parent_node):
        """Move a node to another node's subcanvas"""
        try:
            subcanvas = parent_node.ensure_subcanvas_visible()
            if not subcanvas:
                print(f"Could not get subcanvas from parent node {parent_node}")
                return False

            if child_node.scene():
                child_node.scene().removeItem(child_node)

            child_node.setParentItem(subcanvas)
            child_node.subcanvas_parent = subcanvas

            current_pos = child_node.pos()
            child_node.setPos(current_pos)

            if not hasattr(parent_node, "child_nodes"):
                parent_node.child_nodes = []
            if child_node not in parent_node.child_nodes:
                parent_node.child_nodes.append(child_node)

            print(f"Node moved to subcanvas of {parent_node} at position {current_pos}")
            return True

        except Exception as e:
            print(f"Error moving node to subcanvas: {e}")
            return False

    def _create_composite_internal_node(self, parent_node, model_props):
        """Create internal composite dependency node in subcanvas"""
        try:
            subcanvas = parent_node.ensure_subcanvas_visible()
            if not subcanvas:
                print(
                    f"Could not get subcanvas for composite internal of {parent_node}"
                )
                return False

            if not hasattr(parent_node.model, "get_internal_model"):
                return

            internal_model = parent_node.model.get_internal_model()
            node_type = internal_model.node_type()
            NodeClass = _NODE_MAP.get(node_type)
            if not NodeClass:
                return

            internal_node = NodeClass(0, 0)
            internal_node.model = parent_node.model
            internal_node._independent_model = internal_model

            wrapper = parent_node.model

            def on_model_changed(prop_name, value):
                internal_node.update()

            wrapper.add_change_callback(on_model_changed)

            internal_node.setParentItem(subcanvas)
            offset_x = subcanvas.radius * float(
                model_props.get("internal_position_in_subcanvas_x", 0.6)
            )
            offset_y = subcanvas.radius * float(
                model_props.get("internal_position_in_subcanvas_y", 0.0)
            )
            internal_node.setPos(offset_x, offset_y)
            internal_node.setVisible(True)
            internal_node.subcanvas_parent = subcanvas

            self.nodes.append(internal_node)

            if not hasattr(parent_node, "child_nodes"):
                parent_node.child_nodes = []
            parent_node.child_nodes.append(internal_node)

            print(
                f"Internal composite node '{node_type}' created in "
                f"subcanvas of {parent_node} at ({offset_x:.1f}, "
                f"{offset_y:.1f})"
            )
            return True

        except Exception as e:
            print(f"Error creating internal composite node: {e}")
            import traceback

            traceback.print_exc()
            return False

    def export_to_image(self, filename: str = None) -> bool:
        """Export canvas as PNG image"""
        try:
            if not filename:
                filename, _ = QFileDialog.getSaveFileName(
                    self.canvas,
                    "Export as image",
                    "",
                    "PNG Images (*.png);;JPEG Images (*.jpg *.jpeg)",
                )
                if not filename:
                    return False

                if not filename.endswith(".png"):
                    filename += ".png"

            rect = self.canvas.scene.itemsBoundingRect()
            pixmap = QPixmap(rect.size().toSize())
            pixmap.fill(Qt.GlobalColor.white)

            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            self.canvas.scene.render(painter, source=rect)
            painter.end()

            pixmap.save(filename)
            print(f"Image exported successfully: {filename}")
            return True

        except Exception as e:
            print(f"Error exporting image: {e}")
            QMessageBox.critical(self.canvas, "Error", f"Could not export image:\n{e}")
            return False

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

    def _create_node_from_data(self, node_data: dict) -> object:
        """Create node from serialized data"""
        node_type = node_data["type"]
        pos_data = node_data["position"]

        print(
            f"Creating node {node_type} at position ({pos_data['x']}, {pos_data['y']})"
        )

        node = self.add_node(node_type, 0, 0)
        if not node:
            return None

        node.setPos(float(pos_data["x"]), float(pos_data["y"]))

        if hasattr(node, "model"):
            model_props = node_data.get("model_properties", {})
            if model_props:
                is_composite = model_props.get("is_composite", False)
                if is_composite:
                    ModelClass = _MODEL_MAP.get(node_type)
                    if ModelClass:
                        internal_model = ModelClass(0, 0)
                        internal_model.position_in_subcanvas_x = float(
                            model_props.get("internal_position_in_subcanvas_x", 0.6)
                        )
                        internal_model.position_in_subcanvas_y = float(
                            model_props.get("internal_position_in_subcanvas_y", 0.0)
                        )

                        external_model = node.model
                        wrapper = CompositeModelWrapper(external_model, internal_model)
                        node.model = wrapper
                        node._independent_model = external_model

                        def on_model_changed(prop_name, value):
                            node.update()
                            node.properties_changed.emit(node, {prop_name: value})

                        wrapper.add_change_callback(on_model_changed)

                    wrapper.label = model_props.get("label", "")
                    wrapper.color = model_props.get("color", "#3498db")
                    wrapper.border_color = model_props.get("border_color", "#2980b9")
                    wrapper.text_color = model_props.get("text_color", "#ffffff")

                    external_model = (
                        node._independent_model
                        if hasattr(node, "_independent_model")
                        else node.model
                    )
                    external_model.x = float(model_props.get("x", pos_data["x"]))
                    external_model.y = float(model_props.get("y", pos_data["y"]))
                    external_model.radius = float(model_props.get("radius", 50))
                    external_model.show_subcanvas = model_props.get(
                        "show_subcanvas", False
                    )
                    external_model.position_in_subcanvas_x = float(
                        model_props.get("position_in_subcanvas_x", 0.0)
                    )
                    external_model.position_in_subcanvas_y = float(
                        model_props.get("position_in_subcanvas_y", 0.0)
                    )
                    external_model.content_offset_x = float(
                        model_props.get("content_offset_x", 0.0)
                    )
                    external_model.content_offset_y = float(
                        model_props.get("content_offset_y", 0.0)
                    )
                else:
                    node.model.x = float(model_props.get("x", pos_data["x"]))
                    node.model.y = float(model_props.get("y", pos_data["y"]))
                    node.model.radius = float(model_props.get("radius", 50))
                    node.model.label = model_props.get("label", "")
                    node.model.color = model_props.get("color", "#3498db")
                    node.model.border_color = model_props.get("border_color", "#2980b9")
                    node.model.text_color = model_props.get("text_color", "#ffffff")
                    node.model.show_subcanvas = model_props.get("show_subcanvas", False)
                    node.model.position_in_subcanvas_x = float(
                        model_props.get("position_in_subcanvas_x", 0.0)
                    )
                    node.model.position_in_subcanvas_y = float(
                        model_props.get("position_in_subcanvas_y", 0.0)
                    )
                    node.model.content_offset_x = float(
                        model_props.get("content_offset_x", 0.0)
                    )
                    node.model.content_offset_y = float(
                        model_props.get("content_offset_y", 0.0)
                    )
            else:
                node.model.x = float(pos_data["x"])
                node.model.y = float(pos_data["y"])
                node.model.position_in_subcanvas_x = 0.0
                node.model.position_in_subcanvas_y = 0.0
                node.model.content_offset_x = 0.0
                node.model.content_offset_y = 0.0

        subcanvas_data = node_data.get("subcanvas")
        if subcanvas_data:
            if not hasattr(node, "subcanvas") or node.subcanvas is None:
                node.prepare_subcanvas_for_internal_use()

            if node.subcanvas is not None:
                if "radius" in subcanvas_data:
                    node.subcanvas.radius = float(subcanvas_data["radius"])
                if "original_radius" in subcanvas_data:
                    node.subcanvas.original_radius = float(
                        subcanvas_data["original_radius"]
                    )

                if subcanvas_data.get("visible", False):
                    node.ensure_subcanvas_visible()
                else:
                    node.model.show_subcanvas = False
                    if node.subcanvas:
                        node.subcanvas.setVisible(False)

                if hasattr(node.subcanvas, "_update_handle_pos"):
                    node.subcanvas._update_handle_pos()

        properties = node_data.get("properties", {})
        if hasattr(node, "update_properties"):
            properties["x"] = float(pos_data["x"])
            properties["y"] = float(pos_data["y"])

            if hasattr(node, "model"):
                properties["content_offset_x"] = node.model.content_offset_x
                properties["content_offset_y"] = node.model.content_offset_y
                properties["position_in_subcanvas_x"] = (
                    node.model.position_in_subcanvas_x
                )
                properties["position_in_subcanvas_y"] = (
                    node.model.position_in_subcanvas_y
                )

            node.update_properties(properties)

        if hasattr(node, "is_subcanvas_visible") and node.is_subcanvas_visible():
            if hasattr(node, "apply_position_in_subcanvas"):
                node.apply_position_in_subcanvas()

        node.update()
        print(
            f"Node {node_type} created. Subcanvas position: "
            f"({node.model.position_in_subcanvas_x}, "
            f"{node.model.position_in_subcanvas_y})"
        )
        return node

    def _create_edge_from_data(self, edge_data: dict, node_map: dict):
        """Create edge from serialized data"""
        edge_type = edge_data["type"]
        source_id = edge_data["source_id"]
        target_id = edge_data["target_id"]

        source_node = node_map.get(source_id)
        target_node = node_map.get(target_id)

        if not source_node or not target_node:
            print(
                f"Could not create edge: source({source_id}) or "
                f"target({target_id}) nodes not found"
            )
            return None

        ArrowClass = _ARROW_TYPES.get(edge_type)
        if not ArrowClass:
            print(f"Unknown edge type: {edge_type}")
            return None

        edge_item = ArrowClass(source_node, target_node)
        self.canvas.scene.addItem(edge_item)
        self.edges.append(edge_item)

        properties = edge_data.get("properties", {})
        if hasattr(edge_item, "update_properties"):
            edge_item.update_properties(properties)

        control_points = edge_data.get("control_points", [])
        if control_points and hasattr(edge_item, "control_points"):
            for point_data in control_points:
                point = QPointF(float(point_data["x"]), float(point_data["y"]))
                edge_item.control_points.append(point)
            edge_item._update_handles_position()
            edge_item.update_position()
            edge_item.setSelected(False)
            edge_item.set_handles_visible(False)

        return edge_item

    def _move_edge_to_subcanvas(self, edge, parent_node):
        """Move an edge to another node's subcanvas"""
        try:
            subcanvas = parent_node.ensure_subcanvas_visible()
            if not subcanvas:
                print(f"Could not get subcanvas from parent node {parent_node}")
                return False

            if edge.scene():
                edge.scene().removeItem(edge)

            edge.setParentItem(subcanvas)
            print(f"Edge moved to subcanvas of {parent_node}")
            return True

        except Exception as e:
            print(f"Error moving edge to subcanvas: {e}")
            return False
