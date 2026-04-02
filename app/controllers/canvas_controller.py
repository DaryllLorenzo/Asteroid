# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------
from functools import partial
from typing import Dict, Tuple
import math
import json
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal, Qt, QPointF
from PyQt6.QtGui import QKeySequence, QShortcut, QPixmap, QPainter
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from app.ui.components.entity_item.actor_node_item import ActorNodeItem
from app.ui.components.entity_item.agent_node_item import AgentNodeItem
from app.utils.astr_format import AstrFormat
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
from app.core.models.tropos_element.hard_goal import HardGoal
from app.core.models.tropos_element.soft_goal import SoftGoal
from app.core.models.tropos_element.plan import Plan
from app.core.models.tropos_element.resource import Resource
from app.core.models.composite_model_wrapper import CompositeModelWrapper
from app.ui.components.base_edge_item import BaseEdgeItem
from app.ui.components.control_point_handle import ControlPointHandle

_NODE_MAP = {
    "actor": ActorNodeItem,
    "agent": AgentNodeItem,
    "hard_goal": HardGoalNodeItem,
    "soft_goal": SoftGoalNodeItem,
    "plan": PlanNodeItem,
    "resource": ResourceNodeItem,
}

# Mapeo de clases de modelo (para crear modelos puros sin vista)
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
    "means_end": MeansEndArrowItem
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
        self.current_selection = None

        self._subcanvas_handlers: Dict[object, Tuple[object, callable, callable]] = {}

        # Seguimiento de estado del proyecto
        self._current_file_path = None
        self._is_modified = False

        # conectar señales
        self.canvas.node_dropped.connect(self.add_node)
        self.canvas.arrow_dropped.connect(self.start_arrow_mode)
        self.canvas.node_clicked.connect(self.handle_node_click)

        self.canvas.scene.selectionChanged.connect(self.on_selection_changed)

        # Configurar atajos de teclado para eliminar
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
        """Marca el proyecto como modificado"""
        self.is_modified = True

    def mark_as_saved(self, file_path=None):
        """Marca el proyecto como guardado"""
        self.is_modified = False
        if file_path:
            self._current_file_path = file_path

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
        """Manejar selección considerando subcanvases Y edges - VERSIÓN MEJORADA"""
        selected_items = self.canvas.scene.selectedItems()

        if not selected_items:
            self.selection_changed.emit(None)
            self.selected_node = None
            self.selected_edge = None
            self.current_selection = None
            return

        item = selected_items[0]

        # ✅ VERIFICAR SI ES UN EDGE
        if isinstance(item, BaseEdgeItem):
            print(f"🔗 Edge seleccionado: {item}")
            self.edge_selected.emit(item)
            self.selected_edge = item
            self.selected_node = None
            self.current_selection = item
            self.selection_changed.emit(item)
            return

        # ✅ PARA NODOS: Actualizar referencia ANTES de emitir señales
        old_selected_node = self.selected_node
        self.selected_node = item
        self.selected_edge = None
        self.current_selection = item

        # ✅ SOLO emitir node_selected si el nodo realmente cambió
        if old_selected_node != item:
            print(f"🔧 CanvasController: nodo seleccionado cambiado a {item}")
            self.node_selected.emit(item)

        # Verificar si el nodo está dentro de un subcanvas
        if hasattr(item, 'subcanvas_parent') and item.subcanvas_parent:
            parent_node = item.subcanvas_parent.parentItem()
            if parent_node and hasattr(parent_node, 'subcanvas'):
                if not parent_node.is_subcanvas_visible():
                    parent_node.ensure_subcanvas_visible()

        # ✅ SIEMPRE emitir selection_changed para notificar cambios de selección
        self.selection_changed.emit(item)

    def update_node_properties(self, properties: dict):
        """Actualiza las propiedades del nodo seleccionado"""
        # Usamos current_selection que es lo que actualiza on_selection_changed
        if self.current_selection and hasattr(self.current_selection, 'update_properties'):
            # El modelo recibe los cambios (incluyendo content_offset_x/y)
            self.current_selection.update_properties(properties)
            
            # Forzamos el redibujado para que el translate en paint() se aplique
            self.current_selection.update() 
            
            # Emitir cambio para que el panel de propiedades se sincronice si es necesario
            # Usamos el nombre de señal que ya tienes definido en tu clase: selected_node_properties_changed
            self.selected_node_properties_changed.emit(properties)
            
            # Marcar proyecto como modificado
            self.mark_as_modified()

    # ---------------------
    # agregar nodo global
    # ---------------------

    def add_node(self, node_type: str, x: float, y: float):
        NodeClass = _NODE_MAP.get(node_type)
        if NodeClass is None:
            return None

        # ✅ Crear el nodo sin posición inicial en el modelo
        node_item = NodeClass(0, 0)
        
        # ✅ Establecer posición inmediatamente
        node_item.setPos(x, y)
        
        # ✅ Actualizar el modelo con la posición correcta
        if hasattr(node_item, 'model'):
            node_item.model.x = x
            node_item.model.y = y
        
        self.canvas.scene.addItem(node_item)
        self.nodes.append(node_item)

        if hasattr(node_item, "properties_changed"):
            node_item.properties_changed.connect(self.on_node_properties_changed)
        else:
            print(f"⚠️ Advertencia: El nodo {node_type} no tiene señal properties_changed")

        if hasattr(node_item, "subcanvas_toggled"):
            node_item.subcanvas_toggled.connect(self._on_subcanvas_toggled)

        # Marcar como modificado
        self.mark_as_modified()

        return node_item

    def on_node_properties_changed(self, node_item, properties):
        """Maneja los cambios de propiedades emitidos por los nodos"""
        if node_item == self.selected_node:
            self.selected_node_properties_changed.emit(properties)
            
        if node_item == self.selected_node or (hasattr(node_item, '_resizing') and node_item._resizing):
            self.selected_node_properties_changed.emit(properties)
        
        # Marcar como modificado cuando cambian las propiedades
        self.mark_as_modified()

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
            # CRÍTICO: Recalcular después de setParentItem porque el sistema de coordenadas cambia
            edge_item.update_position()
            print(f"✅ Edge creada dentro de subcanvas: {self._current_subcanvas}")
        else:
            self.canvas.scene.addItem(edge_item)

        self.edges.append(edge_item)

        self._reset_modes()
        for n in self.nodes:
            n.setSelected(False)

        # Marcar como modificado
        self.mark_as_modified()

        return edge_item

    # ---------------------
    # crear composite dependency
    # ---------------------
    def create_composite_dependency(self):
        if len(self.selected_nodes_for_arrow) != 2 or not self.composite_node_type:
            return None

        src, dst = self.selected_nodes_for_arrow
        NodeClass = _NODE_MAP[self.composite_node_type]
        ModelClass = _MODEL_MAP.get(self.composite_node_type)
        
        if not ModelClass:
            print(f"⚠️ No hay modelo para el tipo '{self.composite_node_type}'")
            return None

        # Crear nodo externo (canvas principal)
        mid_x = (src.pos().x() + dst.pos().x()) / 2.0
        mid_y = (src.pos().y() + dst.pos().y()) / 2.0
        
        # Crear modelo externo (puro, sin vista)
        external_model = ModelClass(0, 0)
        external_model.x = mid_x
        external_model.y = mid_y
        
        # Crear modelo interno (para el subcanvas)
        internal_model = ModelClass(0, 0)
        # El modelo interno tendrá posición relativa al subcanvas
        internal_model.position_in_subcanvas_x = 0.6  # 60% del radio hacia la derecha
        internal_model.position_in_subcanvas_y = 0.0
        
        # Crear wrapper que sincroniza ambos modelos
        wrapper = CompositeModelWrapper(external_model, internal_model)
        
        # Agregar callback para redibujar nodos cuando cambien propiedades sincronizadas
        def on_model_changed(prop_name, value):
            # Redibujar ambos nodos
            mid_node.update()
            if hasattr(internal_node, 'update'):
                internal_node.update()
            # Notificar cambio de propiedades para edges conectados
            mid_node.properties_changed.emit(mid_node, {prop_name: value})
        
        wrapper.add_change_callback(on_model_changed)
        
        # Crear nodo externo - inicialmente con modelo normal, luego reemplazamos
        mid_node = NodeClass(0, 0)
        mid_node.setPos(mid_x, mid_y)
        # Reemplazar el modelo con el wrapper
        mid_node.model = wrapper
        # ✅ El nodo externo usa el modelo externo como independiente
        mid_node._independent_model = external_model
        self.canvas.scene.addItem(mid_node)
        self.nodes.append(mid_node)

        # Crear nodo interno - inicialmente con modelo normal, luego reemplazamos
        internal_node = NodeClass(0, 0)
        # Reemplazar el modelo con el wrapper
        internal_node.model = wrapper
        # ✅ IMPORTANTE: Establecer el modelo independiente para radius, posición, etc.
        internal_node._independent_model = internal_model
        
        # Crear edges
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

        # Marcar como modificado
        self.mark_as_modified()

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

        # Marcar como modificado
        self.mark_as_modified()

        return child

    def find_node_by_ui(self, ui_item):
        for n in self.nodes:
            if n is ui_item:
                return n
        return None

    # ---------------------
    # Borrado de elementos
    # ---------------------
    def delete_selected_item(self):
        """
        Elimina el elemento actualmente seleccionado (nodo, edge, o control point).
        Prioridad:
        1. Si hay un ControlPointHandle seleccionado → eliminar ese control point
        2. Si hay un edge seleccionado → eliminar el edge completo
        3. Si hay un nodo seleccionado → eliminar el nodo
        """
        # Verificar si hay un control point seleccionado
        selected_items = self.canvas.scene.selectedItems()
        for item in selected_items:
            if isinstance(item, ControlPointHandle):
                # Eliminar este control point
                self._delete_selected_control_point(item)
                return
        
        # Comportamiento normal
        if self.selected_edge:
            self.delete_selected_edge()
        elif self.selected_node:
            self.delete_selected_node()
        else:
            print("⚠️ No hay elemento seleccionado para eliminar")
    
    def _delete_selected_control_point(self, handle: ControlPointHandle):
        """Elimina un control point específico de un edge"""
        if not handle.parent_edge:
            return
        
        edge = handle.parent_edge
        
        # Encontrar el índice del handle
        try:
            index = edge.control_handles.index(handle)
            # Eliminar el control point correspondiente
            edge.remove_control_point(index)
            # Marcar proyecto como modificado
            self.mark_as_modified()
            print(f"✅ Control point eliminado del edge {edge}")
        except ValueError:
            pass

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
        
        # Marcar como modificado
        self.mark_as_modified()
        
        print(f"✅ Nodo eliminado exitosamente: {node_to_delete}")

    def delete_edge(self, edge_to_delete):
        """Elimina una flecha específica"""
        if edge_to_delete in self.edges:
            # Limpiar handles y desconectar señales primero
            if hasattr(edge_to_delete, 'cleanup'):
                edge_to_delete.cleanup()
            
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

            # Marcar como modificado
            self.mark_as_modified()

            print(f"✅ Flecha eliminada: {edge_to_delete}")
        else:
            print(f"⚠️ Edge no encontrado en la lista: {edge_to_delete}")
    
    def straighten_edge(self, edge):
        """
        Endereza una flecha eliminando todos sus control points.
        """
        if edge and hasattr(edge, 'clear_control_points'):
            edge.clear_control_points()
            self.mark_as_modified()
            print(f"✅ Flecha enderezada: {edge}")

    def _remove_node_from_scene(self, node):
        """Elimina un nodo de la escena de forma segura"""
        if node.scene():
            node.scene().removeItem(node)

    # ---------------------
    # Export/Import
    # ---------------------
    def export_to_astr(self, filename: str = None) -> bool:
        """Exporta el estado actual del canvas a archivo .astr"""
        try:
            if not filename:
                filename, _ = QFileDialog.getSaveFileName(
                    self.canvas, 
                    "Exportar como .astr", 
                    "", 
                    "Asteroid Files (*.astr)"
                )
                if not filename:
                    return False
                
                if not filename.endswith('.astr'):
                    filename += '.astr'
            
            # Serializar escena
            scene_data = AstrFormat.serialize_scene(self.nodes, self.edges)
            
            # Guardar archivo
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(scene_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Proyecto exportado exitosamente: {filename}")
            
            # Marcar como guardado
            self.mark_as_saved(filename)
            
            return True
            
        except Exception as e:
            print(f"❌ Error exportando proyecto: {e}")
            QMessageBox.critical(self.canvas, "Error", f"No se pudo exportar el proyecto:\n{e}")
            return False

    def import_from_astr(self, filename: str = None) -> bool:
        """Importa un proyecto desde archivo .astr - VERSIÓN MEJORADA CON JERARQUÍA COMPLETA"""
        try:
            if not filename:
                filename, _ = QFileDialog.getOpenFileName(
                    self.canvas,
                    "Cargar proyecto .astr",
                    "",
                    "Asteroid Files (*.astr)"
                )
                if not filename:
                    return False

            print(f"🔧 Cargando proyecto desde: {filename}")

            # Cargar archivo
            with open(filename, 'r', encoding='utf-8') as f:
                scene_data = json.load(f)

            print(f"📊 Proyecto contiene: {len(scene_data.get('nodes', []))} nodos, {len(scene_data.get('edges', []))} edges")

            # Limpiar canvas actual
            self.clear_canvas()

            # ✅ PRIMERA PASADA: Crear todos los nodos
            node_map = {}
            parent_child_map = {}  # Mapeo de padres a hijos

            for node_data in scene_data.get('nodes', []):
                print(f"🔧 Procesando nodo {node_data['id']} de tipo {node_data['type']}")
                node = self._create_node_from_data(node_data)
                if node:
                    node_map[node_data['id']] = node

                    # ✅ Guardar información de jerarquía para segunda pasada
                    parent_id = node_data.get('parent_id')
                    if parent_id is not None:
                        if parent_id not in parent_child_map:
                            parent_child_map[parent_id] = []
                        parent_child_map[parent_id].append(node_data['id'])
                        print(f"✅ Nodo {node_data['id']} es hijo de nodo {parent_id}")

            # ✅ SEGUNDA PASADA: Establecer jerarquía (nodos en subcanvas)
            for parent_id, child_ids in parent_child_map.items():
                parent_node = node_map.get(parent_id)
                if parent_node and hasattr(parent_node, 'subcanvas'):
                    print(f"🔧 Moviendo {len(child_ids)} nodos al subcanvas de nodo {parent_id}")
                    for child_id in child_ids:
                        child_node = node_map.get(child_id)
                        if child_node:
                            self._move_node_to_subcanvas(child_node, parent_node)

            # ✅ TERCERA PASADA: Reconstruir edges (TODAS, incluyendo las de subcanvas)
            edge_count = 0
            edge_parent_map = {}  # ✅ Nuevo: mapeo de edges a sus padres

            for edge_data in scene_data.get('edges', []):
                edge = self._create_edge_from_data(edge_data, node_map)
                if edge:
                    edge_count += 1

                    # ✅ Guardar información de parentezco de edges para cuarta pasada
                    parent_id = edge_data.get('parent_id')
                    if parent_id is not None:
                        edge_parent_map[edge] = parent_id
                        print(f"✅ Edge conecta {edge_data['source_id']}->{edge_data['target_id']} en subcanvas de {parent_id}")

            # ✅ CUARTA PASADA: Mover edges a subcanvas si es necesario
            for edge, parent_id in edge_parent_map.items():
                parent_node = node_map.get(parent_id)
                if parent_node and hasattr(parent_node, 'subcanvas'):
                    self._move_edge_to_subcanvas(edge, parent_node)

            # ✅ QUINTA PASADA: Vincular nodos composite internos con externos
            # Esto debe hacerse DESPUÉS de crear los edges para poder buscar el target
            composite_nodes = {}  # id -> node_data mapping
            
            for node_data in scene_data.get('nodes', []):
                model_props = node_data.get('model_properties', {})
                if model_props.get('is_composite', False):
                    # ✅ Solo considerar nodos externos (los que NO tienen parent_id)
                    parent_id = node_data.get('parent_id')
                    if parent_id is None:
                        composite_nodes[node_data['id']] = node_data
            
            # Para cada nodo composite externo, buscar su interno y vincularlos
            linked_internal_nodes = set()  # Para evitar vincular el mismo nodo interno dos veces
            
            for node_id, node_data in composite_nodes.items():
                external_node = node_map.get(node_id)
                if not external_node:
                    continue
                
                model_props = node_data.get('model_properties', {})
                
                # ✅ El nodo interno está en el subcanvas del DESTINO de la flecha (target)
                # Necesitamos encontrar el edge que sale de este nodo composite para saber el destino
                target_node = None
                for edge in self.edges:
                    if edge.source_node == external_node:
                        target_node = edge.dest_node
                        break
                
                if not target_node:
                    print(f"⚠️ No se encontró edge saliente para nodo composite {node_id}")
                    continue
                
                # Buscar el nodo interno en el subcanvas del target
                if hasattr(target_node, 'subcanvas') and target_node.subcanvas:
                    # Buscar el nodo interno en el subcanvas
                    internal_node = None
                    
                    # ✅ Obtener posición interna esperada (puede ser diferente para cada nodo)
                    expected_x = target_node.subcanvas.radius * float(model_props.get('internal_position_in_subcanvas_x', 0.6))
                    expected_y = target_node.subcanvas.radius * float(model_props.get('internal_position_in_subcanvas_y', 0.0))
                    
                    # ✅ Buscar todos los nodos del mismo tipo en el subcanvas
                    candidates = []
                    for child in target_node.subcanvas.childItems():
                        # ✅ Evitar nodos ya vinculados
                        if id(child) in linked_internal_nodes:
                            continue
                        
                        if isinstance(child, type(external_node)) and hasattr(child, 'model'):
                            candidates.append(child)
                    
                    # ✅ Si hay múltiples candidatos, buscar el más cercano a la posición esperada
                    if len(candidates) == 1:
                        internal_node = candidates[0]
                        print(f"🔍 Nodo interno encontrado (único candidato) en subcanvas de {target_node}")
                    elif len(candidates) > 1:
                        # Buscar el más cercano a la posición esperada
                        min_dist = float('inf')
                        for candidate in candidates:
                            dist = abs(candidate.pos().x() - expected_x) + abs(candidate.pos().y() - expected_y)
                            if dist < min_dist:
                                min_dist = dist
                                internal_node = candidate
                        print(f"🔍 Nodo interno encontrado en subcanvas de {target_node} (distancia={min_dist:.1f})")
                    else:
                        print(f"⚠️ No se encontraron nodos del tipo {type(external_node).__name__} en subcanvas de {target_node}")
                    
                    if internal_node:
                        # Marcar como vinculado
                        linked_internal_nodes.add(id(internal_node))
                        
                        # Crear wrapper y vincular ambos nodos
                        ModelClass = _MODEL_MAP.get(node_data['type'])
                        if ModelClass:
                            # ✅ PRESERVAR radio interno antes de crear el wrapper
                            internal_radius = internal_node._independent_model.radius if hasattr(internal_node, '_independent_model') else getattr(internal_node.model, 'radius', 50)
                            
                            # Crear modelo interno con los datos serializados
                            new_internal_model = ModelClass(0, 0)
                            new_internal_model.position_in_subcanvas_x = float(model_props.get('internal_position_in_subcanvas_x', 0.6))
                            new_internal_model.position_in_subcanvas_y = float(model_props.get('internal_position_in_subcanvas_y', 0.0))
                            # ✅ Preservar radio interno
                            new_internal_model.radius = internal_radius
                            
                            # El modelo externo es el que ya tiene el nodo externo
                            external_model = external_node.model
                            
                            # Crear wrapper
                            wrapper = CompositeModelWrapper(external_model, new_internal_model)
                            
                            # Actualizar ambos nodos con el wrapper
                            external_node.model = wrapper
                            external_node._independent_model = external_model
                            
                            internal_node.model = wrapper
                            internal_node._independent_model = new_internal_model
                            
                            # ✅ Actualizar propiedades sincronizadas a través del wrapper
                            wrapper.label = model_props.get('label', '')
                            wrapper.color = model_props.get('color', '#3498db')
                            wrapper.border_color = model_props.get('border_color', '#2980b9')
                            wrapper.text_color = model_props.get('text_color', '#ffffff')
                            
                            # ✅ Actualizar radio independiente del nodo externo
                            external_model.radius = float(model_props.get('radius', 50))
                            
                            # Forzar redibujado inicial
                            external_node.update()
                            internal_node.update()
                            
                            # Agregar callbacks
                            def on_external_changed(prop_name, value):
                                external_node.update()
                                external_node.properties_changed.emit(external_node, {prop_name: value})
                            
                            def on_internal_changed(prop_name, value):
                                internal_node.update()
                            
                            wrapper.add_change_callback(on_external_changed)
                            wrapper.add_change_callback(on_internal_changed)
                            
                            print(f"✅ Nodo composite interno vinculado con externo (radio externo={external_model.radius}, interno={internal_radius})")
                    else:
                        print(f"⚠️ No se encontró nodo interno en subcanvas de {target_node}")
                else:
                    print(f"⚠️ Target {target_node} no tiene subcanvas")

            print(f"✅ Proyecto cargado exitosamente: {filename}")
            print(f"📊 Resumen: {len(node_map)} nodos, {edge_count} edges reconstruidos")

            # Marcar como guardado (no modificado)
            self.mark_as_saved(filename)

            return True

        except Exception as e:
            print(f"❌ Error cargando proyecto: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self.canvas, "Error", f"No se pudo cargar el proyecto:\n{e}")
            return False

    def _move_node_to_subcanvas(self, child_node, parent_node):
        """Mueve un nodo al subcanvas de otro nodo padre"""
        try:
            # Preparar subcanvas del padre
            subcanvas = parent_node.ensure_subcanvas_visible()
            if not subcanvas:
                print(f"❌ No se pudo obtener subcanvas del nodo padre {parent_node}")
                return False
            
            # Remover nodo hijo de la escena principal
            if child_node.scene():
                child_node.scene().removeItem(child_node)
            
            # Agregar nodo hijo al subcanvas
            child_node.setParentItem(subcanvas)
            child_node.subcanvas_parent = subcanvas
            
            # Mantener la posición relativa
            current_pos = child_node.pos()
            child_node.setPos(current_pos)
            
            # Agregar a la lista de hijos del padre
            if not hasattr(parent_node, 'child_nodes'):
                parent_node.child_nodes = []
            if child_node not in parent_node.child_nodes:
                parent_node.child_nodes.append(child_node)
            
            print(f"✅ Nodo movido al subcanvas de {parent_node} en posición {current_pos}")
            return True

        except Exception as e:
            print(f"❌ Error moviendo nodo a subcanvas: {e}")
            return False

    def _create_composite_internal_node(self, parent_node, model_props):
        """Crea el nodo interno de un composite dependency en el subcanvas"""
        try:
            # Preparar subcanvas del padre
            subcanvas = parent_node.ensure_subcanvas_visible()
            if not subcanvas:
                print(f"❌ No se pudo obtener subcanvas para composite interno de {parent_node}")
                return False

            # Obtener el modelo interno del wrapper
            if not hasattr(parent_node.model, 'get_internal_model'):
                return
            
            internal_model = parent_node.model.get_internal_model()
            node_type = internal_model.node_type()
            NodeClass = _NODE_MAP.get(node_type)
            if not NodeClass:
                return

            # Crear nodo interno con el wrapper como modelo
            internal_node = NodeClass(0, 0)
            internal_node.model = parent_node.model  # Compartir el wrapper
            # ✅ IMPORTANTE: Establecer el modelo independiente para radius, posición, etc.
            internal_node._independent_model = internal_model
            
            # Agregar callback para redibujar nodo interno cuando cambien propiedades sincronizadas
            wrapper = parent_node.model
            def on_model_changed(prop_name, value):
                internal_node.update()
            
            wrapper.add_change_callback(on_model_changed)

            # Posicionar en el subcanvas
            internal_node.setParentItem(subcanvas)
            offset_x = subcanvas.radius * float(model_props.get('internal_position_in_subcanvas_x', 0.6))
            offset_y = subcanvas.radius * float(model_props.get('internal_position_in_subcanvas_y', 0.0))
            internal_node.setPos(offset_x, offset_y)
            internal_node.setVisible(True)
            internal_node.subcanvas_parent = subcanvas

            self.nodes.append(internal_node)

            if not hasattr(parent_node, "child_nodes"):
                parent_node.child_nodes = []
            parent_node.child_nodes.append(internal_node)

            print(f"✅ Nodo composite interno '{node_type}' creado en subcanvas de {parent_node} en ({offset_x:.1f}, {offset_y:.1f})")
            return True

        except Exception as e:
            print(f"❌ Error creando nodo composite interno: {e}")
            import traceback
            traceback.print_exc()
            return False

    def export_to_image(self, filename: str = None) -> bool:
        """Exporta el canvas como imagen PNG"""
        try:
            if not filename:
                filename, _ = QFileDialog.getSaveFileName(
                    self.canvas,
                    "Exportar como imagen",
                    "",
                    "PNG Images (*.png);;JPEG Images (*.jpg *.jpeg)"
                )
                if not filename:
                    return False

                if not filename.endswith('.png'):
                    filename += '.png'

            # Obtener el rectángulo que contiene todos los items
            rect = self.canvas.scene.itemsBoundingRect()
            
            # Crear pixmap
            pixmap = QPixmap(rect.size().toSize())
            pixmap.fill(Qt.GlobalColor.white)
            
            # Renderizar escena en el pixmap
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            self.canvas.scene.render(painter, source=rect)
            painter.end()
            
            # Guardar imagen
            pixmap.save(filename)
            
            print(f"✅ Imagen exportada exitosamente: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Error exportando imagen: {e}")
            QMessageBox.critical(self.canvas, "Error", f"No se pudo exportar la imagen:\n{e}")
            return False

    def clear_canvas(self):
        """Limpia completamente el canvas"""
        # Limpiar selecciones
        self.selected_node = None
        self.selected_edge = None
        self.current_selection = None
        
        # Remover todos los edges
        for edge in self.edges[:]:
            if edge.scene():
                edge.scene().removeItem(edge)
        self.edges.clear()
        
        # Remover todos los nodos
        for node in self.nodes[:]:
            if node.scene():
                node.scene().removeItem(node)
        self.nodes.clear()
        
        # Limpiar selección de la escena
        self.canvas.scene.clearSelection()
        
        # Marcar como no modificado (proyecto nuevo)
        self.is_modified = False
        self._current_file_path = None
        
        print("✅ Canvas limpiado")

    def _create_node_from_data(self, node_data: Dict) -> object:
        """Crea un nodo a partir de datos serializados - VERSIÓN CON SOPORTE DE POSICIÓN EN SUBCANVAS"""
        node_type = node_data['type']
        pos_data = node_data['position']

        print(f"🔧 Creando nodo {node_type} en posición ({pos_data['x']}, {pos_data['y']})")

        # ✅ CREAR el nodo en la posición CERO primero
        node = self.add_node(node_type, 0, 0)
        if not node:
            return None

        # ✅ LUEGO establecer la posición real en el Canvas
        node.setPos(float(pos_data['x']), float(pos_data['y']))

        # ✅ ACTUALIZAR el modelo con la posición correcta y otras propiedades
        if hasattr(node, 'model'):
            model_props = node_data.get('model_properties', {})
            if model_props:
                # Verificar si es un nodo composite
                is_composite = model_props.get('is_composite', False)

                if is_composite:
                    # Crear modelo interno para el subcanvas
                    ModelClass = _MODEL_MAP.get(node_type)
                    if ModelClass:
                        internal_model = ModelClass(0, 0)
                        internal_model.position_in_subcanvas_x = float(model_props.get('internal_position_in_subcanvas_x', 0.6))
                        internal_model.position_in_subcanvas_y = float(model_props.get('internal_position_in_subcanvas_y', 0.0))

                        # Guardar modelo externo original antes de crear wrapper
                        external_model = node.model
                        
                        # Crear wrapper - el modelo externo es el que ya tiene el nodo
                        wrapper = CompositeModelWrapper(external_model, internal_model)
                        node.model = wrapper
                        # ✅ El nodo externo usa su modelo original como independiente
                        node._independent_model = external_model

                        # Agregar callback para redibujar nodos cuando cambien propiedades sincronizadas
                        def on_model_changed(prop_name, value):
                            node.update()
                            node.properties_changed.emit(node, {prop_name: value})

                        wrapper.add_change_callback(on_model_changed)
                    
                    # ✅ Actualizar propiedades sincronizadas a través del wrapper
                    wrapper.label = model_props.get('label', '')
                    wrapper.color = model_props.get('color', '#3498db')
                    wrapper.border_color = model_props.get('border_color', '#2980b9')
                    wrapper.text_color = model_props.get('text_color', '#ffffff')
                    
                    # ✅ Propiedades independientes en el modelo externo
                    external_model = node._independent_model if hasattr(node, '_independent_model') else node.model
                    external_model.x = float(model_props.get('x', pos_data['x']))
                    external_model.y = float(model_props.get('y', pos_data['y']))
                    external_model.radius = float(model_props.get('radius', 50))
                    external_model.show_subcanvas = model_props.get('show_subcanvas', False)
                    external_model.position_in_subcanvas_x = float(model_props.get('position_in_subcanvas_x', 0.0))
                    external_model.position_in_subcanvas_y = float(model_props.get('position_in_subcanvas_y', 0.0))
                    external_model.content_offset_x = float(model_props.get('content_offset_x', 0.0))
                    external_model.content_offset_y = float(model_props.get('content_offset_y', 0.0))
                else:
                    # Nodo normal (no composite)
                    node.model.x = float(model_props.get('x', pos_data['x']))
                    node.model.y = float(model_props.get('y', pos_data['y']))
                    node.model.radius = float(model_props.get('radius', 50))
                    node.model.label = model_props.get('label', '')
                    node.model.color = model_props.get('color', '#3498db')
                    node.model.border_color = model_props.get('border_color', '#2980b9')
                    node.model.text_color = model_props.get('text_color', '#ffffff')
                    node.model.show_subcanvas = model_props.get('show_subcanvas', False)

                    # 🚀 NUEVO: Recuperar la posición del nodo dentro de su subcanvas
                    node.model.position_in_subcanvas_x = float(model_props.get('position_in_subcanvas_x', 0.0))
                    node.model.position_in_subcanvas_y = float(model_props.get('position_in_subcanvas_y', 0.0))

                    # ✅ Mantener también los offsets de contenido interno
                    node.model.content_offset_x = float(model_props.get('content_offset_x', 0.0))
                    node.model.content_offset_y = float(model_props.get('content_offset_y', 0.0))
            else:
                # Fallback a los valores básicos si no hay model_properties
                node.model.x = float(pos_data['x'])
                node.model.y = float(pos_data['y'])
                node.model.position_in_subcanvas_x = 0.0
                node.model.position_in_subcanvas_y = 0.0
                node.model.content_offset_x = 0.0
                node.model.content_offset_y = 0.0

        # ✅ RESTAURAR estado del subcanvas (Lógica existente mantenida)
        subcanvas_data = node_data.get('subcanvas')
        if subcanvas_data:
            if not hasattr(node, 'subcanvas') or node.subcanvas is None:
                node.prepare_subcanvas_for_internal_use()

            if node.subcanvas is not None:
                if 'radius' in subcanvas_data:
                    node.subcanvas.radius = float(subcanvas_data['radius'])
                if 'original_radius' in subcanvas_data:
                    node.subcanvas.original_radius = float(subcanvas_data['original_radius'])

                if subcanvas_data.get('visible', False):
                    node.ensure_subcanvas_visible()
                else:
                    node.model.show_subcanvas = False
                    if node.subcanvas:
                        node.subcanvas.setVisible(False)

                if hasattr(node.subcanvas, '_update_handle_pos'):
                    node.subcanvas._update_handle_pos()

        # ✅ APLICAR propiedades adicionales y forzar actualización visual
        properties = node_data.get('properties', {})
        if hasattr(node, 'update_properties'):
            properties['x'] = float(pos_data['x'])
            properties['y'] = float(pos_data['y'])

            # 🚀 Asegurarnos de que el diccionario de propiedades lleve ambos tipos de offsets
            if hasattr(node, 'model'):
                properties['content_offset_x'] = node.model.content_offset_x
                properties['content_offset_y'] = node.model.content_offset_y
                properties['position_in_subcanvas_x'] = node.model.position_in_subcanvas_x
                properties['position_in_subcanvas_y'] = node.model.position_in_subcanvas_y

            node.update_properties(properties)

        # 🚀 APLICAR posición física en subcanvas después de crear el nodo completamente
        if hasattr(node, 'is_subcanvas_visible') and node.is_subcanvas_visible():
            if hasattr(node, 'apply_position_in_subcanvas'):
                node.apply_position_in_subcanvas()

        # Forzar el redibujado
        node.update()

        print(f"✅ Nodo {node_type} creado y posicionado. Posición en subcanvas: ({node.model.position_in_subcanvas_x}, {node.model.position_in_subcanvas_y})")
        return node

    def _create_edge_from_data(self, edge_data: Dict, node_map: Dict):
        """Crea una edge a partir de datos serializados - VERSIÓN MEJORADA"""
        edge_type = edge_data['type']
        source_id = edge_data['source_id']
        target_id = edge_data['target_id']

        source_node = node_map.get(source_id)
        target_node = node_map.get(target_id)

        if not source_node or not target_node:
            print(f"⚠️ No se pudo crear edge: nodos fuente({source_id}) o destino({target_id}) no encontrados")
            return None

        # Crear edge
        ArrowClass = _ARROW_TYPES.get(edge_type)
        if not ArrowClass:
            print(f"⚠️ Tipo de edge desconocido: {edge_type}")
            return None

        edge_item = ArrowClass(source_node, target_node)

        # ✅ POR AHORA agregar a la escena principal, luego se moverá si es necesario
        self.canvas.scene.addItem(edge_item)
        self.edges.append(edge_item)

        # Aplicar propiedades
        properties = edge_data.get('properties', {})
        if hasattr(edge_item, 'update_properties'):
            edge_item.update_properties(properties)
        
        # Restaurar control points si existen
        control_points = edge_data.get('control_points', [])
        if control_points and hasattr(edge_item, 'control_points'):
            for point_data in control_points:
                point = QPointF(float(point_data['x']), float(point_data['y']))
                edge_item.control_points.append(point)
            # Actualizar handles después de restaurar todos los puntos
            edge_item._update_handles_position()
            edge_item.update_position()
            # ✅ Asegurar que el edge y sus handles NO estén seleccionados al cargar
            edge_item.setSelected(False)
            # ✅ IMPORTANTE: Ocultar handles explícitamente (el edge no está seleccionado)
            edge_item.set_handles_visible(False)

        return edge_item

    def _move_edge_to_subcanvas(self, edge, parent_node):
        """Mueve una edge al subcanvas de otro nodo padre"""
        try:
            # Preparar subcanvas del padre
            subcanvas = parent_node.ensure_subcanvas_visible()
            if not subcanvas:
                print(f"❌ No se pudo obtener subcanvas del nodo padre {parent_node}")
                return False

            # Remover edge de la escena principal
            if edge.scene():
                edge.scene().removeItem(edge)

            # Agregar edge al subcanvas
            edge.setParentItem(subcanvas)

            print(f"✅ Edge movida al subcanvas de {parent_node}")
            return True

        except Exception as e:
            print(f"❌ Error moviendo edge a subcanvas: {e}")
            return False