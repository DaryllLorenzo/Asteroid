# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------
from PyQt6.QtWidgets import QGraphicsItem

from app.commands.add_edge_command import AddEdgeCommand
from app.controller_types import CanvasNodeItem
from app.controllers._canvas_mixin import CanvasControllerMixin
from app.controllers.canvas_registry_controller import _ARROW_TYPES
from app.controllers.canvas_registry_controller import _MODEL_MAP
from app.controllers.canvas_registry_controller import _NODE_MAP
from app.core.models.composite_model_wrapper import CompositeModelWrapper
from app.ui.components.base_edge_item import BaseEdgeItem
from app.ui.components.base_node_item import BaseNodeItem
from app.ui.components.base_tropos_item import BaseTroposItem
from app.ui.components.dependency_item.dependency_link_edge_item import (
    DependencyLinkArrowItem,
)
from app.ui.components.entity_item.actor_node_item import ActorNodeItem
from app.ui.components.entity_item.agent_node_item import AgentNodeItem


class CanvasInteractionController(CanvasControllerMixin):
    arrow_mode: bool
    selected_arrow_type: str | None
    selected_nodes_for_arrow: list[CanvasNodeItem]
    composite_mode: bool
    composite_node_type: str | None

    def start_arrow_mode(
        self,
        arrow_type: str,
    ) -> None:
        if arrow_type not in _ARROW_TYPES:
            return
        self._reset_modes()
        self.arrow_mode = True
        self.selected_arrow_type = arrow_type
        print(f"CanvasController: start global arrow mode '{arrow_type}'")

    def start_composite_dependency_mode(
        self,
        node_type: str,
    ) -> None:
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

    def _reset_modes(self) -> None:
        self.arrow_mode = False
        self.selected_arrow_type = None
        self.selected_nodes_for_arrow = []
        self.composite_mode = False
        self.composite_node_type = None
        self._current_subcanvas = None

    def handle_node_click(
        self,
        node_item: object,
    ) -> None:
        if self.selection_mode:
            return

        if isinstance(node_item, BaseEdgeItem):
            node_item = node_item.source_node

        if self.composite_mode:
            self._handle_composite_mode_click(node_item)
            return

        if self.arrow_mode:
            if isinstance(node_item, (BaseNodeItem, BaseTroposItem)):
                self._handle_arrow_mode_click(node_item)

    def _handle_composite_mode_click(
        self,
        node_item: object,
    ) -> None:
        node = self._find_parent_actor_agent(node_item)
        if node is None:
            print("CanvasController: composite mode only accepts Actor/Agent; ignored.")
            return

        if node not in self.selected_nodes_for_arrow:
            self.selected_nodes_for_arrow.append(node)
            node.setSelected(True)

        if len(self.selected_nodes_for_arrow) == 2:
            self.create_composite_dependency()

    def _find_parent_actor_agent(
        self,
        node_item: object,
    ) -> CanvasNodeItem | None:
        node = node_item if isinstance(node_item, QGraphicsItem) else None
        while node is not None and not isinstance(node, (ActorNodeItem, AgentNodeItem)):
            node = node.parentItem()
        return node

    def _handle_arrow_mode_click(
        self,
        node_item: CanvasNodeItem,
    ) -> None:
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

    def _start_subarrow_mode(
        self,
        parent_node_item: CanvasNodeItem,
        subcanvas,
        arrow_type: str,
    ) -> None:
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

        parent = self._current_subcanvas if self._current_subcanvas else None

        self.undo_stack.push(AddEdgeCommand(self, edge_item, parent))

        self._reset_modes()
        for node in self.nodes:
            node.setSelected(False)

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
        scene = self.canvas.scene()
        if scene is None:
            return None

        scene.addItem(mid_node)
        self.nodes.append(mid_node)

        internal_node = NodeClass(0, 0)
        internal_node.model = wrapper
        internal_node._independent_model = internal_model

        e1 = DependencyLinkArrowItem(src, mid_node)
        e2 = DependencyLinkArrowItem(mid_node, dst)
        scene.addItem(e1)
        scene.addItem(e2)
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
