# canvas_controller.py
# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------

from functools import partial
from typing import Dict, Tuple
import math

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QKeySequence, QShortcut

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


class CanvasController(QObject):
    node_selected = pyqtSignal(object)
    selected_node_properties_changed = pyqtSignal(dict)
    node_deleted = pyqtSignal(object)
    edge_selected = pyqtSignal(object)
    edge_deleted = pyqtSignal(object)
    selection_changed = pyqtSignal(object)  # ✅ Nueva señal unificada para cualquier selección

    def __init__(self, canvas):
        super().__init__()
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

        self._current_subcanvas = None

        # modo seleccion para edicion (solo afecta interacción)
        self.selection_mode = False
        self.selected_node = None
        self.selected_edge = None
        self.current_selection = None  # ✅ Referencia unificada al elemento seleccionado

        self._subcanvas_handlers: Dict[object, Tuple[object, callable, callable]] = {}

        # conectar señales
        self.canvas.node_dropped.connect(self.add_node)
        self.canvas.arrow_dropped.connect(self.start_arrow_mode)
        self.canvas.node_clicked.connect(self.handle_node_click)

        self.canvas.scene.selectionChanged.connect(self.on_selection_changed)

        # ✅ Configurar atajos de teclado para eliminar
        self._setup_delete_shortcut()

    def _setup_delete_shortcut(self):
        """Configura el atajo de teclado para eliminar elementos seleccionados"""
        self.delete_shortcut = QShortcut(QKeySequence("Delete"), self.canvas)
        self.delete_shortcut.activated.connect(self.delete_selected_item)
        
        self.delete_shortcut2 = QShortcut(QKeySequence("Ctrl+D"), self.canvas)
        self.delete_shortcut2.activated.connect(self.delete_selected_item)

    def set_selection_mode(self, enabled):
        """Activa/desactiva el modo selección"""
        self.selection_mode = enabled
        
        if not enabled:
            self.canvas.scene.clearSelection()
            self.selected_node = None
            self.selected_edge = None
            self.current_selection = None

    def on_selection_changed(self):
        """Manejar selección considerando subcanvases Y edges"""
        selected_items = self.canvas.scene.selectedItems()

        if not selected_items:
            self.selection_changed.emit(None)  # ✅ Emitir None cuando no hay selección
            return

        item = selected_items[0]

        # ✅ VERIFICAR SI ES UN EDGE
        if isinstance(item, BaseEdgeItem):
            self.edge_selected.emit(item)
            self.selected_edge = item
            self.selected_node = None
            self.current_selection = item  # ✅ Guardar referencia unificada
            self.selection_changed.emit(item)  # ✅ Emitir señal unificada
            print(f"🔗 Edge seleccionado: {item}")
            return

        # ✅ Verificar si el nodo está dentro de un subcanvas
        if hasattr(item, 'subcanvas_parent') and item.subcanvas_parent:
            self.node_selected.emit(item)
            self.selected_node = item
            self.selected_edge = None
            self.current_selection = item  # ✅ Guardar referencia unificada

            parent_node = item.subcanvas_parent.parentItem()
            if parent_node and hasattr(parent_node, 'subcanvas'):
                if not parent_node.is_subcanvas_visible():
                    parent_node.ensure_subcanvas_visible()
        else:
            self.node_selected.emit(item)
            self.selected_node = item
            self.selected_edge = None
            self.current_selection = item  # ✅ Guardar referencia unificada

        self.selection_changed.emit(item)  # ✅ Emitir señal unificada

    def update_node_properties(self, properties: dict):
        """Actualiza las propiedades del nodo seleccionado"""
        if self.selected_node and hasattr(self.selected_node, 'update_properties'):
            self.selected_node.update_properties(properties)

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

        if hasattr(node_item, "properties_changed"):
            node_item.properties_changed.connect(self.on_node_properties_changed)
        else:
            print(f"⚠️ Advertencia: El nodo {node_type} no tiene señal properties_changed")

        if hasattr(node_item, "subcanvas_toggled"):
            node_item.subcanvas_toggled.connect(self._on_subcanvas_toggled)

        return node_item

    def on_node_properties_changed(self, node_item, properties):
        """Maneja los cambios de propiedades emitidos por los nodos"""
        if node_item == self.selected_node:
            self.selected_node_properties_changed.emit(properties)
            
        if node_item == self.selected_node or (hasattr(node_item, '_resizing') and node_item._resizing):
            self.selected_node_properties_changed.emit(properties)

    # ---------------------
    # iniciar modo flecha global
    # ---------------------
    def start_arrow_mode(self, arrow_type: str):
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
        if self.selection_mode:
            return

        if isinstance(node_item, BaseEdgeItem):
            node_item = node_item.source_node

        if self.composite_mode:
            original_node = node_item
            while node_item is not None and not isinstance(node_item, (ActorNodeItem, AgentNodeItem)):
                node_item = node_item.parentItem()
            
            if node_item is None or not isinstance(node_item, (ActorNodeItem, AgentNodeItem)):
                print("CanvasController: composite mode - only Actor/Agent selectable; ignored.")
                return

            if node_item not in self.selected_nodes_for_arrow:
                self.selected_nodes_for_arrow.append(node_item)
                node_item.setSelected(True)

            if len(self.selected_nodes_for_arrow) == 2:
                self.create_composite_dependency()
            return

        if not self.arrow_mode:
            return

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

        self._reset_modes()
        for n in self.nodes:
            n.setSelected(False)

        return edge_item

    # ---------------------
    # crear composite dependency
    # ---------------------
    def create_composite_dependency(self):
        if len(self.selected_nodes_for_arrow) != 2 or not self.composite_node_type:
            return None

        src, dst = self.selected_nodes_for_arrow
        NodeClass = _NODE_MAP[self.composite_node_type]

        mid_x = (src.pos().x() + dst.pos().x()) / 2.0
        mid_y = (src.pos().y() + dst.pos().y()) / 2.0
        mid_node = NodeClass(0, 0)
        mid_node.setPos(mid_x, mid_y)
        self.canvas.scene.addItem(mid_node)
        self.nodes.append(mid_node)

        e1 = DependencyLinkArrowItem(src, mid_node)
        e2 = DependencyLinkArrowItem(mid_node, dst)
        self.canvas.scene.addItem(e1)
        self.canvas.scene.addItem(e2)
        self.edges.extend([e1, e2])

        subcanvas = None
        if hasattr(dst, "prepare_subcanvas_for_internal_use"):
            subcanvas = dst.prepare_subcanvas_for_internal_use()
        else:
            print("⚠️ El nodo destino no soporta subcanvas, se omite la inserción interna.")

        if subcanvas:
            internal_node = NodeClass(0, 0)
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

            print(f"✅ Composite: nodo '{self.composite_node_type}' agregado al subcanvas de {dst} en ({offset_x:.1f}, {offset_y:.1f})")

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
        child.subcanvas_parent = subcanvas
    
        self.nodes.append(child)
    
        if hasattr(child, "properties_changed"):
            child.properties_changed.connect(self.on_node_properties_changed)
        else:
            print(f"⚠️ Advertencia: nodo interno {item_type} no tiene properties_changed")
    
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

    def find_node_by_ui(self, ui_item):
        for n in self.nodes:
            if n is ui_item:
                return n
        return None
    
    # ---------------------
    # Borrado de elementos
    # ---------------------
    def delete_selected_item(self):
        """Elimina el elemento actualmente seleccionado (nodo o edge)"""
        if self.selected_edge:
            self.delete_selected_edge()
        elif self.selected_node:
            self.delete_selected_node()
        else:
            print("⚠️ No hay elemento seleccionado para eliminar")

    def delete_selected_node(self):
        """Elimina el nodo actualmente seleccionado"""
        if not self.selected_node:
            print("⚠️ No hay nodo seleccionado para eliminar")
            return
        
        print(f"🗑️ Eliminando nodo: {self.selected_node}")
        self.delete_node(self.selected_node)

    def delete_selected_edge(self):
        """Elimina el edge actualmente seleccionado"""
        if not self.selected_edge:
            print("⚠️ No hay edge seleccionado para eliminar")
            return
        
        print(f"🗑️ Eliminando edge: {self.selected_edge}")
        self.delete_edge(self.selected_edge)

    def delete_node(self, node_to_delete):
        """Elimina un nodo específico y todas sus conexiones"""
        if node_to_delete not in self.nodes:
            # Si no está en la lista pero está en la escena, eliminarlo directamente
            if node_to_delete.scene():
                print(f"✅ Eliminando nodo directamente de la escena (no estaba en lista)")
                self._remove_node_from_scene(node_to_delete)
                return
            else:
                print(f"❌ Nodo no encontrado y no está en escena: {node_to_delete}")
                return

        print(f"🗑️ Eliminando nodo: {node_to_delete}")

        # Eliminar todas las flechas conectadas a este nodo
        edges_to_remove = []
        for edge in self.edges[:]:
            if edge.source_node == node_to_delete or edge.dest_node == node_to_delete:
                edges_to_remove.append(edge)
        
        for edge in edges_to_remove:
            self.delete_edge(edge)

        # Si el nodo tiene hijos, eliminarlos también
        if hasattr(node_to_delete, 'child_nodes') and node_to_delete.child_nodes:
            print(f"🔍 Eliminando {len(node_to_delete.child_nodes)} nodos hijos...")
            child_nodes_copy = node_to_delete.child_nodes.copy()
            for child_node in child_nodes_copy:
                self.delete_node(child_node)

        # Eliminar subcanvas
        if hasattr(node_to_delete, 'subcanvas') and node_to_delete.subcanvas:
            if node_to_delete.subcanvas.scene():
                node_to_delete.scene().removeItem(node_to_delete.subcanvas)
            node_to_delete.subcanvas = None

        # Remover el nodo de la escena y de la lista
        self._remove_node_from_scene(node_to_delete)
        
        if node_to_delete in self.nodes:
            self.nodes.remove(node_to_delete)

        # Limpiar selección
        if node_to_delete == self.selected_node:
            self.selected_node = None
            self.current_selection = None
            self.node_selected.emit(None)
            self.selection_changed.emit(None)

        self.node_deleted.emit(node_to_delete)
        
        print(f"✅ Nodo eliminado exitosamente: {node_to_delete}")

    def delete_edge(self, edge_to_delete):
        """Elimina una flecha específica"""
        if edge_to_delete in self.edges:
            if edge_to_delete.scene():
                edge_to_delete.scene().removeItem(edge_to_delete)
            self.edges.remove(edge_to_delete)
            
            # Limpiar selección
            if edge_to_delete == self.selected_edge:
                self.selected_edge = None
                self.current_selection = None
                self.edge_selected.emit(None)
                self.selection_changed.emit(None)
                
            self.edge_deleted.emit(edge_to_delete)
            print(f"✅ Flecha eliminada: {edge_to_delete}")
        else:
            print(f"⚠️ Edge no encontrado en la lista: {edge_to_delete}")

    def _remove_node_from_scene(self, node):
        """Elimina un nodo de la escena de forma segura"""
        if node.scene():
            node.scene().removeItem(node)