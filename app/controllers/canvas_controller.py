# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------

# app/controllers/canvas_controller.py
from functools import partial
from typing import Dict, Tuple
import math

from app.ui.components.entity_item.actor_node_item import ActorNodeItem
from app.ui.components.entity_item.agent_node_item import AgentNodeItem

from app.ui.components.dependency_item.simple_edge_item import SimpleArrowItem
from app.ui.components.dependency_item.dashed_edge_item import DashedArrowItem
from app.ui.components.dependency_item.dependency_link_edge_item import DependencyLinkArrowItem
from app.ui.components.dependency_item.why_link_edge_item import WhyLinkArrowItem
from app.ui.components.dependency_item.or_decomposition_edge_item import OrDecompositionArrowItem
from app.ui.components.dependency_item.and_decomposition_edge_item import AndDecompositionArrowItem
from app.ui.components.dependency_item.contribution_edge_item import ContributionArrowItem
from app.ui.components.dependency_item.means_end_edge_item import MeansEndArrowItem

from app.ui.components.tropos_element_item.hard_goal_item import HardGoalNodeItem
from app.ui.components.tropos_element_item.plan_item import PlanNodeItem
from app.ui.components.tropos_element_item.resource_item import ResourceNodeItem
from app.ui.components.tropos_element_item.soft_goal_item import SoftGoalNodeItem
from app.ui.components.base_edge_item import BaseEdgeItem

_NODE_MAP = {
    "actor": ActorNodeItem,
    "agent": AgentNodeItem,
    "hard_goal": HardGoalNodeItem,
    "soft_goal": SoftGoalNodeItem,
    "plan": PlanNodeItem,
    "resource": ResourceNodeItem,
}

_ARROW_TYPES = {
    "simple": SimpleArrowItem,
    "dashed": DashedArrowItem,
    "dependency_link": DependencyLinkArrowItem,
    "why_link": WhyLinkArrowItem,
    "or_decomposition": OrDecompositionArrowItem,
    "and_decomposition": AndDecompositionArrowItem,
    "contribution": ContributionArrowItem,
    "means_end": MeansEndArrowItem
}


class CanvasController:
    def __init__(self, canvas):
        self.canvas = canvas
        self.nodes = []
        self.edges = []

        self.arrow_mode = False
        self.selected_arrow_type = None
        self.selected_nodes_for_arrow = []
        self._current_subcanvas = None  # subcanvas activo, si hay

        # parent_node -> (subcanvas, handler_node, handler_arrow)
        self._subcanvas_handlers: Dict[object, Tuple[object, callable, callable]] = {}

        # conectar señales
        self.canvas.node_dropped.connect(self.add_node)
        self.canvas.arrow_dropped.connect(self.start_arrow_mode)
        self.canvas.node_clicked.connect(self.handle_node_click)

    # ---------------------
    # agregar nodo global
    # ---------------------
    def add_node(self, node_type: str, x: float, y: float):
        NodeClass = _NODE_MAP.get(node_type)
        if NodeClass is None:
            return None

        node_item = NodeClass(0, 0)
        node_item.setPos(x, y)
        self.canvas.scene.addItem(node_item)
        self.nodes.append(node_item)

        if hasattr(node_item, "subcanvas_toggled"):
            node_item.subcanvas_toggled.connect(self._on_subcanvas_toggled)

        return node_item

    # ---------------------
    # iniciar modo flecha global
    # ---------------------
    def start_arrow_mode(self, arrow_type: str):
        if arrow_type not in _ARROW_TYPES:
            return
        self.arrow_mode = True
        self.selected_arrow_type = arrow_type
        self.selected_nodes_for_arrow = []
        self._current_subcanvas = None
        print(f"CanvasController: start global arrow mode '{arrow_type}'")

    # ---------------------
    # manejar click en nodo
    # ---------------------
    def handle_node_click(self, node_item):
        if not self.arrow_mode:
            return

        # Si es un edge, redirigir al nodo origen
        if isinstance(node_item, BaseEdgeItem):
            print(f"Clicked on an edge, redirecting to its source node {node_item.source_node}")
            node_item = node_item.source_node

        node_subcanvas = getattr(node_item, "subcanvas_parent", None)
        print(f"Clicked node {node_item}, subcanvas_parent={node_subcanvas}, current_subcanvas={self._current_subcanvas}")

        # Validar si estamos en un subcanvas activo
        if self._current_subcanvas:
            if node_subcanvas is not self._current_subcanvas:
                print("CanvasController: node not in current subcanvas, ignored")
                return

        if node_item not in self.selected_nodes_for_arrow:
            self.selected_nodes_for_arrow.append(node_item)
            node_item.setSelected(True)

        if len(self.selected_nodes_for_arrow) == 2:
            self.create_arrow()


    # ---------------------
    # crear flecha
    # ---------------------
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
        else:
            self.canvas.scene.addItem(edge_item)

        self.edges.append(edge_item)

        # reset
        self.arrow_mode = False
        self.selected_arrow_type = None
        self.selected_nodes_for_arrow = []
        self._current_subcanvas = None

        # limpiar selección
        for n in self.nodes:
            n.setSelected(False)

        return edge_item

    # ---------------------
    # subcanvas
    # ---------------------
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
        self._subcanvas_handlers[parent_node_item] = (subcanvas, handler_node, handler_arrow)

        try:
            subcanvas.setZValue(parent_node_item.zValue() - 1)
        except Exception:
            pass

    def _add_to_subcanvas(self, parent_node_item, subcanvas, item_type: str, local_x: float, local_y: float):
        NodeClass = _NODE_MAP.get(item_type)
        if NodeClass is None:
            return None

        child = NodeClass(0, 0, radius=20)
        if child.scene() is not None and child.parentItem() is None:
            child.scene().removeItem(child)

        child.setParentItem(subcanvas)
        child.setPos(local_x, local_y)
        child.setVisible(subcanvas.isVisible())

        # registrar el subcanvas padre en el nodo
        child.subcanvas_parent = subcanvas

        if not hasattr(parent_node_item, "child_nodes"):
            parent_node_item.child_nodes = []
        parent_node_item.child_nodes.append(child)

        return child

    def _start_subarrow_mode(self, parent_node_item, subcanvas, arrow_type: str):
        if arrow_type not in _ARROW_TYPES:
            return
        self.arrow_mode = True
        self.selected_arrow_type = arrow_type
        self.selected_nodes_for_arrow = []
        self._current_subcanvas = subcanvas
        print(f"CanvasController: start subarrow mode '{arrow_type}' in {subcanvas}")

    # ---------------------
    # util
    # ---------------------
    def find_node_by_ui(self, ui_item):
        for n in self.nodes:
            if n is ui_item:
                return n
        return None
