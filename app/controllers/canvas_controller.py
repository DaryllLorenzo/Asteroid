# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------

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

        # modos
        self.arrow_mode = False
        self.selected_arrow_type = None
        self.selected_nodes_for_arrow = []

        # composite mode
        self.composite_mode = False
        self.composite_node_type = None

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
        # arrow_type puede ser una clave en _ARROW_TYPES
        if arrow_type not in _ARROW_TYPES:
            return
        self._reset_modes()
        self.arrow_mode = True
        self.selected_arrow_type = arrow_type
        print(f"CanvasController: start global arrow mode '{arrow_type}'")

    # ---------------------
    # iniciar modo composite (desde sidebar)
    # ---------------------
    def start_composite_dependency_mode(self, node_type: str):
        if node_type not in _NODE_MAP:
            print(f"CanvasController: unknown composite node_type '{node_type}'")
            return
        self._reset_modes()
        self.composite_mode = True
        self.composite_node_type = node_type
        self.selected_nodes_for_arrow = []
        print(f"CanvasController: start composite mode for '{node_type}'. Click two Actor/Agent nodes.")

    def _reset_modes(self):
        # limpia los modos (no resetea selection visual de nodos)
        self.arrow_mode = False
        self.selected_arrow_type = None
        self.selected_nodes_for_arrow = []
        self.composite_mode = False
        self.composite_node_type = None
        self._current_subcanvas = None

    # ---------------------
    # manejar click en nodo
    # ---------------------
    def handle_node_click(self, node_item):
        # si el usuario clickea un edge, redirigimos al source node (conveniencia)
        if isinstance(node_item, BaseEdgeItem):
            node_item = node_item.source_node
    
        # Si estamos en modo composite priorizamos eso
        if self.composite_mode:
            original_node = node_item
            # Buscar hacia arriba hasta encontrar un Actor/Agent
            while node_item is not None and not isinstance(node_item, (ActorNodeItem, AgentNodeItem)):
                node_item = node_item.parentItem()
            
            # Si no encontramos un Actor/Agent, ignoramos
            if node_item is None or not isinstance(node_item, (ActorNodeItem, AgentNodeItem)):
                print("CanvasController: composite mode - only Actor/Agent selectable; ignored.")
                return
    
            if node_item not in self.selected_nodes_for_arrow:
                self.selected_nodes_for_arrow.append(node_item)
                node_item.setSelected(True)
    
            if len(self.selected_nodes_for_arrow) == 2:
                self.create_composite_dependency()
            return  # no procesar modo flecha normal
    
        # Si no estamos en modo flecha, ignorar
        if not self.arrow_mode:
            return
    
        # modo flecha normal
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

    # ---------------------
    # crear flecha normal entre dos nodos
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
        self._reset_modes()
        # limpiar selección visual de nodos
        for n in self.nodes:
            n.setSelected(False)

        return edge_item

       # ---------------------
    # crear composite dependency (actor/agent -> tropos_node -> actor/agent)
    # ---------------------
    def create_composite_dependency(self):
        if len(self.selected_nodes_for_arrow) != 2 or not self.composite_node_type:
            return None

        src, dst = self.selected_nodes_for_arrow
        NodeClass = _NODE_MAP[self.composite_node_type]

        # nodo intermedio global
        mid_x = (src.pos().x() + dst.pos().x()) / 2.0
        mid_y = (src.pos().y() + dst.pos().y()) / 2.0
        mid_node = NodeClass(0, 0)
        mid_node.setPos(mid_x, mid_y)
        self.canvas.scene.addItem(mid_node)
        self.nodes.append(mid_node)

        # Crear flechas globales
        e1 = DependencyLinkArrowItem(src, mid_node)
        e2 = DependencyLinkArrowItem(mid_node, dst)
        self.canvas.scene.addItem(e1)
        self.canvas.scene.addItem(e2)
        self.edges.extend([e1, e2])

        # ✅ Preparar subcanvas SIN mostrarlo
        subcanvas = None
        if hasattr(dst, "prepare_subcanvas_for_internal_use"):
            subcanvas = dst.prepare_subcanvas_for_internal_use()
        else:
            print("⚠️ El nodo destino no soporta subcanvas, se omite la inserción interna.")

        # ✅ Crear nodo interno en el subcanvas (si existe), FUERA DEL CENTRO
        if subcanvas:
            internal_node = NodeClass(0, 0)
            internal_node.setParentItem(subcanvas)
            
            # Posicionar en un lugar visible pero no centrado
            # Ej: a la derecha, dentro del círculo
            offset_x = subcanvas.radius * 0.6
            offset_y = 0
            internal_node.setPos(offset_x, offset_y)
            
            internal_node.setVisible(True)
            internal_node.subcanvas_parent = subcanvas

            if not hasattr(dst, "child_nodes"):
                dst.child_nodes = []
            dst.child_nodes.append(internal_node)

            print(f"✅ Composite: nodo '{self.composite_node_type}' agregado al subcanvas de {dst} en ({offset_x:.1f}, {offset_y:.1f})")

        # 🔥 Deseleccionar nodos y salir del modo compuesto
        for node in self.selected_nodes_for_arrow:
            node.setSelected(False)

        self._reset_modes()
        return (mid_node, e1, e2)


    # ---------------------
    # subcanvas management
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
        self._reset_modes()
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
